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
    'LA1':{'Temp':0.0,'Updated':''},
    'LA2':{'Temp':0.0,'Updated':''},
    'VA1':{'Temp':0.0,'Updated':''},
    'VA2':{'Temp':0.0,'Updated':''},
    'VA3':{'Temp':0.0,'Updated':''},
    'LH': {'Temp':0.0,'Updated':''},
    'OD1':{'Temp':0.0,'Updated':''},
    'Water':{'Temp':0.0,'Updated':''}
}

def print_sensors():
    for sensor in sensors:
        print(sensor)


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
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


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
							sensors[fields[1]]['Temp'] = fields[3]
					
					
					print (sensors)
					print(text, fields)
				print(f"{ts}  {text}")
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
