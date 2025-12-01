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
from tkinter import simpledialog
from threading import Thread
import time
from datetime import datetime
from datetime import timedelta
import json

try:
    import serial
    from serial.serialutil import SerialException
except Exception as e:
    print("Missing dependency: pyserial. Install with: pip install pyserial")
    raise

sensors = {
    
    'LA1_T':    {'Sensor': 'Lilla Astrid  ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'LA2_T':    {'Sensor': 'Studio        ', 'Type':'Temp','Value':0.0, 'Min':14.0, 'Max': 28.0, 'Updated':''},
    'VA1_T':    {'Sensor': 'MH1           ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'VA1_H':    {'Sensor': 'MH1           ', 'Type':'Hum', 'Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'VA2_T':    {'Sensor': 'MH2           ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'VA3_T':    {'Sensor': 'Parvi         ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'LH_T':     {'Sensor': 'Lilla Astrid  ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'OD1_T':    {'Sensor': 'Outdoor       ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''},
    'Water_T':  {'Sensor': 'Vesi -1m      ', 'Type':'Temp','Value':0.0, 'Min':10.0, 'Max': 30.0, 'Updated':''}
}

with open("sensor_dict.json","w") as fp:
    json.dump(sensors,fp)

msg_tags = list(sensors.keys())
print (msg_tags)
nbr_of_sensors = len(msg_tags)

def print_sensors():
    print("{0:8s} {1:14s} {2:6s} {3:4s} {4}".format('Sensor','Location','Value', 'Hum', 'Updated'))
    for key in sensors.keys():
        # print ("{0:8s} {1:12s} {2:4.1f} {3:4.0f} {4}".format(key, sensors[key]['Sensor'], sensors[key]['Temp'], sensors[key]['Hum'],sensors[key]['Updated']))
        print(format_sensor(key))

def format_sensor(key) -> str:
    s = "{0:8s} {1:12s}".format(key, sensors[key]['Sensor'], )
    if 'Type' in sensors[key].keys():
        if sensors[key]['Type'] == 'Temp':       
            s = s + " Temp {0:4.1f}C ".format(sensors[key]['Value'])
        elif sensors[key]['Type'] == 'Hum':       
            s = s + " Hum {0:4.0f}KPa ".format(sensors[key]['Value'])
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
        if diff.total_seconds() > 45:
            status = SENSOR_STATUS_OUTDATED
        elif sensors[key]['Value'] < sensors[key]['Min']:
            status = SENSOR_STATUS_LOW_TEMPERATURE
        elif sensors[key]['Value'] > sensors[key]['Max']:
            status = SENSOR_STATUS_HIGH_TEMPERATURE
            
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

def open_config_window(root, tag):
    selected_tag =tag
    conf_window = tk.Toplevel(root)
    conf_window.title = ('Configurate:',tag)
    conf_window.geometry('600x400')

    #tk.Label(conf_window, text=f"Tag: {tag}").pack(side=tk.LEFT,pady=5)
    #fields = []
    #for i in range(3):
    #    tk.Label(conf_window, text=f"Field {i+1}:").pack()
    #    entry = tk.Entry(conf_window)
    #    entry.pack(pady=5)
    #    fields.append(entry)
    print(tag,sensors[tag]['Min'],sensors[tag]['Max'])
    label_sensor = tk.Label(conf_window, text=tag+sensors[tag]['Sensor'], font=('Arial',12))
    label_sensor.grid(row=0,column=1,pady=10, sticky='w')
    
    
    var_max = tk.StringVar(value=sensors[tag]['Max'])
    label_max_value = tk.Label(conf_window, text="Max Value", font=('Arial',12))
    label_max_value.grid(row=1,column=0,pady=10, sticky='w')
    entry_max_value = tk.Entry(conf_window, textvariable = var_max, width=30)
    entry_max_value.grid(row=1,column=1,pady=5, padx=10)

    var_min = tk.StringVar(value=sensors[tag]['Min'])
    label_min_value = tk.Label(conf_window, text="Min Value", font=('Arial',12))
    label_min_value.grid(row=2,column=0,pady=10, sticky='w')
    entry_min_value = tk.Entry(conf_window, textvariable = var_min, width=30)
    entry_min_value.grid(row=2,column=1,pady=5, padx=10)
         
    def accept_min():
        sensors[tag]['Min'] = entry_min_value.get()

    def accept_max():
        sensors[tag]['Max'] = entry_max_value.get()

    def accept():
        values = [field.get() for field in fields]
        print(f"Values: {values}")
        conf_window.destroy()
        
    def exit_window():
        conf_window.destroy();

    btn_max_value = tk.Button(conf_window, text='Accept', command = accept_max)
    btn_max_value.grid(row=1,column=2,pady=10, padx=10)
    btn_min_value = tk.Button(conf_window, text='Accept', command = accept_min)
    btn_min_value.grid(row=2,column=2,pady=10, padx=10)

    btn_exit = tk.Button(conf_window, text='Exit', command=exit_window)
    btn_exit.grid(row=3,column=2,pady=10, padx=10)

    
    #button_frame = tk.Frame(conf_window)
    #button_frame.pack(pady=10)
    #tk.Button(button_frame, text='Accept', command=accept).pack(side=tk.LEFT,padx=5)
    #tk.Button(button_frame, text='Exit', command=exit_window).pack(side=tk.LEFT,padx=5)

             
             
             
             
             
             
             
             
             
             
             


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
                    print(fields)
                    if fields[1] in sensors:
                        if fields[2] == sensors[fields[1]]['Type']:
                            # sensors[fields[1]]['Temp'] = float(fields[3])
                            try:
                                sensors[fields[1]]['Value'] = float(fields[3])
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
        # https://www.plus2net.com/python/tkinter-colors.php
        for i in range(nbr_of_sensors):
            sensor_status =  get_sensor_status(msg_tags[i])
            if sensor_status == SENSOR_STATUS_OK:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='green',fg='white')
            elif sensor_status == SENSOR_STATUS_NO_DATA:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='grey',fg='black')
            elif sensor_status == SENSOR_STATUS_OUTDATED:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='chocolate',fg='black')
            elif sensor_status == SENSOR_STATUS_LOW_TEMPERATURE:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='cyan',fg='black')
            elif sensor_status == SENSOR_STATUS_HIGH_TEMPERATURE:
                labels[i].config(text=format_sensor(msg_tags[i]),bg='crimson',fg='gold1')
        #labels[0].config(text=format_sensor('VA1'))
            #labels[1].config(text=f"Double: {counter * 2}")
        #labels[2].config(text=f"Square: {counter ** 2}")
        #labels[3].config(text=f"Time: {time.time():.2f}")
        #counter += 1
        time.sleep(1)



DIM_WIDTH = 800
DIM_HEIGHT = 600
DIM_ROWS  = 16
DIM_ROW_WIDTH = 500
DIM_ROW_HEIGHT = 40
DIM_BTN_X0     = DIM_ROW_WIDTH +10
DIM_BTN_WIDTH  = DIM_WIDTH - DIM_ROW_WIDTH -20


def cb_verify(tag):
    print(tag)

def main() -> int:
    #read_messages(ser)

    root = tk.Tk()
    root.title("Villa Astrid Control Room")
    geom = "{0}x{1}".format(DIM_WIDTH,DIM_HEIGHT)
    root.geometry(geom)

    labels = []
    buttons = []
    for i in range(nbr_of_sensors):
        label = tk.Label(root, text="Updating...", font=("Arial", 12))
        # label.pack(anchor=tk.W, pady=5, width=200)
        label.place(x=0, y=i*DIM_ROW_HEIGHT, width=DIM_ROW_WIDTH, height=DIM_ROW_HEIGHT)
        labels.append(label)
        # btn = tk.Button(root,text='OK', command=lambda tag = msg_tags[i]: cb_verify(tag))
        btn = tk.Button(root,text='OK', command=lambda tag = msg_tags[i]: open_config_window(root,tag))
        btn.place(x=DIM_BTN_X0, y=i*DIM_ROW_HEIGHT, width=DIM_BTN_WIDTH, height=DIM_ROW_HEIGHT)
        buttons.append(btn)

    # Start update loop in a separate thread
    thread = Thread(target=update_loop, args=(root, labels), daemon=True)
    thread.start()

    root.mainloop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
