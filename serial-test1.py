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
import time
from datetime import datetime

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

def pretty_print_dict(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty_print_dict(value, indent+1)
        else:
            print('\t' * (indent + 1) + str(value))


def print_sensors():
    print("{0:8s} {1:14s} {2:6s} {3:4s} {4}".format('Sensor','Location','Temp', 'Hum', 'Updated'))
    for key in sensors.keys():
        print ("{0:8s} {1:12s} {2:4.1f} {3:4.0f} {4}".format(key, sensors[key]['Sensor'], sensors[key]['Temp'], sensors[key]['Hum'],sensors[key]['Updated']))


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
    #return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def main() -> int:
    args = parse_args()

    print(f"Starting serial reader on port={args.port} baud={args.baud} timeout={args.timeout}")

    try:
        ser = open_serial(args.port, args.baud, args.timeout)
    except Exception:
        return 2

    try:
        # Read loop
        while True:
            if True:
                # readline() returns bytes; decode with errors replaced
                line = ser.readline()
                if not line:
                    continue
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
                                sensors[fields[1]]['Updated'] = ts
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
