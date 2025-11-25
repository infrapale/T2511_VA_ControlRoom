import serial
import RPi.GPIO as GPIO
import time

# Raspberry Pi GPIO UART Configuration
# GPIO 14 (TXD) - Pin 8
# GPIO 15 (RXD) - Pin 10
# Ground      - Pin 6

class RaspberryPiSerial:
    def __init__(self, device='/dev/serial0', baudrate=9600):
        """
        /dev/serial0 - Primary UART (GPIO 14/15)
        /dev/ttyAMA0 - Hardware UART (Pi 3/4)
        /dev/ttyS0 - Mini UART (Pi 3/4)
        """
        self.device = device
        self.baudrate = baudrate
        self.serial = None
        
    def connect(self):
        """Connect to Raspberry Pi UART"""
        try:
            self.serial = serial.Serial(
                port=self.device,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False
            
    def send_command(self, command):
        """Send command and read response"""
        if not self.serial:
            return None
            
        self.serial.write(command.encode() + b'\r\n')
        time.sleep(0.1)
        
        response = b''
        while self.serial.in_waiting:
            response += self.serial.read(self.serial.in_waiting)
            time.sleep(0.1)
            
        return response.decode().strip()
        
    def close(self):
        if self.serial:
            self.serial.close()

# Basic usage
pi_serial = RaspberryPiSerial('/dev/serial0', 115200)
if pi_serial.connect():
    response = pi_serial.send_command('AT')
    print(f"Response: {response}")
    pi_serial.close()