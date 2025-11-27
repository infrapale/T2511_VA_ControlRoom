#!/usr/bin/env python3
"""
Simple Raspberry Pi serial (RX) reader.

Reads from a serial device (default `/dev/serial0`) and prints received
lines with timestamps. Designed to run on a Raspberry Pi using the
primary UART or a USB-serial adapter.

Usage:
  python3 serial-test1.py --port /dev/ttyUSB0 --baud 115200

Environment variables (optional):
  SERIAL_PORT  - serial device path (overrides --port)
  SERIAL_BAUD  - baud rate (overrides --baud)

Requires: pyserial
"""

from __future__ import annotations

import argparse
import os
import sys
import tkinter as tk
from threading import Thread
import time
from datetime import datetime
from datetime import timedelta

try:
    import serial
    from serial.serialutil import SerialException
except Exception as e:
    print("Missing dependency: pyserial. Install with: pip install pyserial")
    raise

sensors = {
    'LA1':    {'Sensor': 'Lilla Astrid  ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'LA2':    {'Sensor': 'Studio        ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA1':    {'Sensor': 'MH1           ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA2':    {'Sensor': 'MH2           ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA3':    {'Sensor': 'Parvi         ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'LH':     {'Sensor': 'Lilla Astrid  ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'OD1':    {'Sensor': 'Outdoor       ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'Water':  {'Sensor': 'Vesi -1m      ', 'Temp':0.0, 'Hum':0.0, 'Updated':''}
}

msg_tags = list(sensors.keys())
print (msg_tags)
nbr_of_sensors = len(msg_tags)

def print_sensors():
    print("{0:8s} {1:14s} {2:6s} {3:4s} {4}".format('Sensor','Location','Temp', 'Hum', 'Updated'))
    for key in sensors.keys():
        # print ("{0:8s} {1:12s} {2:4.1f} {3:4.0f} {4}".format(key, sensors[key]['Sensor'], sensors[key]['Temp'], sensors[key]['Hum'],sensors[key]['Updated']))
        print(format_sensor(key))

def format_sensor(key) -> str:
    s = "{0:8s} {1:12s} {2:4.1f} {3:4.0f}".format(key, sensors[key]['Sensor'], sensors[key]['Temp'], sensors[key]['Hum'])
    try:
        s = s + "  < {0}".format(sensors[key]['Updated'].strftime("%Y-%m-%d %H:%M:%S"))
    except:
        s = s + "  < ---"
    return (s)

SENSOR_STATUS_OK = 0
SENSOR_STATUS_NO_DATA = 1
SENSOR_STATUS_OUTDATED = 2
SENSOR_STATUS_HIGH_TEMPERATURE = 3
SENSOR_STATUS_LOW_TEMPERATURE = 4

def get_sensor_status(key):
    status = SENSOR_STATUS_OK
    if sensors[key]['Updated']:
        status = SENSOR_STATUS_OK 
        diff = datetime.now() - sensors[key]['Updated']
        if diff.total_seconds() > 15:
            status = SENSOR_STATUS_OUTDATED
    else:
        status = SENSOR_STATUS_NO_DATA
    return (status) 


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Raspberry Pi serial RX reader")
    p.add_argument("--port", "-p", default=os.getenv("SERIAL_PORT", "/dev/serial0"),
                   help="Serial device (default from $SERIAL_PORT or /dev/serial0)")
    p.add_argument("--baud", "-b", type=int, default=int(os.getenv("SERIAL_BAUD", "9600")),
                   help="Baud rate (default from $SERIAL_BAUD or 9600)")
    p.add_argument("--timeout", "-t", type=float, default=1.0,
                   help="Read timeout in seconds (default 1.0)")
    p.add_argument("--hex", action="store_true",
                   help="Print incoming bytes as hex instead of UTF-8 decoded lines")
    return p.parse_args()


def open_serial(port: str, baud: int, timeout: float) -> serial.Serial:
    try:
        ser = serial.Serial(port=port, baudrate=baud, timeout=timeout)
        return ser
    except SerialException as e:
        print(f"Failed to open serial port {port}: {e}")
        raise


def format_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")[:-3]

def parse_line(line):
    try:
        # Read loop
        if True:
            # readline() returns bytes; decode with errors replaced
            #line = ser.readline()
            if line:
                ts = format_ts()
                try:
                    text = line.decode("utf-8", errors="replace").rstrip("\r\n")
                except Exception:
                    text = repr(line)
                if((text[0] == '<') and (text[-1] == '>')):
                    print(text)
                    text = text[1:-1]
                    fields = text.split(';')
                    
                    if fields[1] in sensors:
                        if fields[2] in sensors[fields[1]]:
                            # sensors[fields[1]]['Temp'] = float(fields[3])
                            try:
                                sensors[fields[1]][fields[2]] = float(fields[3])
                                sensors[fields[1]]['Updated'] = datetime.now()
                            except:
                                pass
                            
                            
                    print_sensors()
                    #print (sensors)
                    #print(text, fields)
                #print(f"{ts}  {text}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user, closing serial port...")
    except SerialException as e:
        print(f"Serial error: {e}")
    finally:
        try:
            ser.close()
        except Exception:
            pass


def update_loop(root, labels):
    args = parse_args()
    
    """Loop that updates labels from outside the window"""
    counter = 0
    try:
        ser = open_serial(args.port, args.baud, args.timeout)
        print(f"Started serial reader on port={args.port} baud={args.baud} timeout={args.timeout}")
    except Exception:
        print('open_serial() failed')
        return 2

    while True:
        line = ser.readline()
        if line:
            print(line)
        parse_line(line)
        #labels[0].config(text=f"Counter: {counter}")
        for i in range(nbr_of_sensors):
            sensor_status =  get_sensor_status(msg_tags[i])
            if sensor_status == SENSOR_STATUS_OK:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='green',fg='white')
            elif sensor_status == SENSOR_STATUS_NO_DATA:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='grey',fg='black')
            elif sensor_status == SENSOR_STATUS_OUTDATED:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='orange',fg='black')
        #labels[0].config(text=format_sensor('VA1'))
        #labels[1].config(text=f"Double: {counter * 2}")
        #labels[2].config(text=f"Square: {counter ** 2}")
        #labels[3].config(text=f"Time: {time.time():.2f}")
        #counter += 1
        time.sleep(1)




def main() -> int:
    #read_messages(ser)

    root = tk.Tk()
    root.title("Villa Astrid Control Room")
    root.geometry("480x400")

    # Create 4 labels
    labels = []
    for i in range(nbr_of_sensors):
        label = tk.Label(root, text="Updating...", font=("Arial", 12))
        label.pack(anchor=tk.W, pady=5)
        labels.append(label)

    # Start update loop in a separate thread
    thread = Thread(target=update_loop, args=(root, labels), daemon=True)
    thread.start()

    root.mainloop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
