"""
Simple Tkinter UI that displays several text fields which can be updated
by incoming data. Includes a simulator that pushes updates into a queue and
an optional serial-send feature for a Raspberry Pi using pyserial.

Run:
	python3 tkinter_ai_test_1.py

Dependencies (optional serial):
	pip install -r requirements.txt

Edit the serial device and baudrate in the UI to match your Raspberry Pi
setup (for example `/dev/serial0` or `/dev/ttyUSB0`).
"""

import threading
import queue
import time
import random
import json
import tkinter as tk
from tkinter import ttk

try:
	import serial
	SERIAL_AVAILABLE = True
except Exception:
	SERIAL_AVAILABLE = False


class TkDataPanel:
	def __init__(self, root):
		self.root = root
		root.title("Data Panel")

		self.fields = [
			"Temperature (C)",
			"Humidity (%)",
			"Pressure (hPa)",
			"Device Status",
			"Message",
		]

		self.vars = {name: tk.StringVar(value="-") for name in self.fields}

		main = ttk.Frame(root, padding=12)
		main.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

		for idx, name in enumerate(self.fields):
			ttk.Label(main, text=name).grid(column=0, row=idx, sticky=tk.W, pady=2)
			ent = ttk.Entry(main, textvariable=self.vars[name], width=30, state="readonly")
			ent.grid(column=1, row=idx, sticky=(tk.W, tk.E), pady=2)

		controls = ttk.Frame(main, padding=(0, 8, 0, 0))
		controls.grid(column=0, row=len(self.fields), columnspan=2, sticky=(tk.W, tk.E))

		# Simulation controls
		self.sim_running = False
		self.sim_button = ttk.Button(controls, text="Start Simulation", command=self.toggle_simulation)
		self.sim_button.grid(column=0, row=0, sticky=tk.W)

		# Serial controls
		self.serial_enabled = tk.BooleanVar(value=False)
		self.serial_check = ttk.Checkbutton(controls, text="Enable Serial Send", variable=self.serial_enabled)
		self.serial_check.grid(column=1, row=0, sticky=tk.W, padx=8)

		ttk.Label(controls, text="Port:").grid(column=0, row=1, sticky=tk.W, pady=4)
		self.serial_port_var = tk.StringVar(value="/dev/serial0")
		ttk.Entry(controls, textvariable=self.serial_port_var, width=18).grid(column=1, row=1, sticky=tk.W)

		ttk.Label(controls, text="Baud:").grid(column=0, row=2, sticky=tk.W, pady=4)
		self.serial_baud_var = tk.IntVar(value=115200)
		ttk.Entry(controls, textvariable=self.serial_baud_var, width=18).grid(column=1, row=2, sticky=tk.W)

		send_now = ttk.Button(controls, text="Send Current over Serial", command=self.send_current_over_serial)
		send_now.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E), pady=(6, 0))

		# Queue and threading
		self.incoming_queue = queue.Queue()
		self._sim_thread = None
		self._stop_event = threading.Event()

		# Serial handle
		self.serial_handle = None

		# Start periodic queue processing
		self.root.after(100, self._process_queue)

		# Ensure clean shutdown
		self.root.protocol("WM_DELETE_WINDOW", self._on_close)

	def toggle_simulation(self):
		if not self.sim_running:
			self.sim_running = True
			self.sim_button.config(text="Stop Simulation")
			self._stop_event.clear()
			self._sim_thread = threading.Thread(target=self._simulation_producer, daemon=True)
			self._sim_thread.start()
		else:
			self.sim_running = False
			self.sim_button.config(text="Start Simulation")
			self._stop_event.set()

	def _simulation_producer(self):
		while not self._stop_event.is_set():
			data = {
				"Temperature (C)": round(random.uniform(15.0, 30.0), 1),
				"Humidity (%)": round(random.uniform(20.0, 80.0), 1),
				"Pressure (hPa)": round(random.uniform(980.0, 1030.0), 1),
				"Device Status": random.choice(["OK", "WARN", "ERROR"]),
				"Message": random.choice(["Idle", "Running", "Sleeping", "Update"]),
			}
			# Put JSON string to simulate incoming payloads, or raw dict
			self.incoming_queue.put(data)
			time.sleep(1.0)

	def _process_queue(self):
		try:
			while True:
				item = self.incoming_queue.get_nowait()
				self.update_fields(item)
		except queue.Empty:
			pass
		finally:
			self.root.after(100, self._process_queue)

	def update_fields(self, data):
		# data can be dict or JSON string
		if isinstance(data, str):
			try:
				data = json.loads(data)
			except Exception:
				data = {"Message": data}

		for key, value in data.items():
			if key in self.vars:
				self.vars[key].set(str(value))

		# Optionally send to serial
		if self.serial_enabled.get():
			payload = json.dumps(data)
			self._serial_send(payload)

	def _open_serial(self):
		if not SERIAL_AVAILABLE:
			return None
		if self.serial_handle is None:
			try:
				self.serial_handle = serial.Serial(self.serial_port_var.get(), self.serial_baud_var.get(), timeout=1)
			except Exception as exc:
				print(f"Failed to open serial port: {exc}")
				self.serial_handle = None
		return self.serial_handle

	def _serial_send(self, text):
		if not SERIAL_AVAILABLE:
			print("pyserial not installed; cannot send to serial.")
			return
		handle = self._open_serial()
		if handle is None:
			return
		try:
			if isinstance(text, str):
				to_write = (text + "\n").encode("utf-8")
			else:
				to_write = (json.dumps(text) + "\n").encode("utf-8")
			handle.write(to_write)
		except Exception as exc:
			print(f"Serial write failed: {exc}")

	def send_current_over_serial(self):
		data = {k: self.vars[k].get() for k in self.fields}
		self._serial_send(json.dumps(data))

	def _on_close(self):
		self._stop_event.set()
		# Give threads a moment to stop
		if self._sim_thread is not None:
			self._sim_thread.join(timeout=1.0)
		if self.serial_handle is not None:
			try:
				self.serial_handle.close()
			except Exception:
				pass
		self.root.destroy()


def main():
	root = tk.Tk()
	# Make UI scale nicely
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	app = TkDataPanel(root)
	root.mainloop()


if __name__ == "__main__":
	main()
