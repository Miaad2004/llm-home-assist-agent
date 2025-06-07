import serial
import time

# Set up the serial connection (adjust baudrate to match your Arduino sketch)
arduino = serial.Serial(port='COM10', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# Write data to Arduino
arduino.write(b'10:1\n')  # Must be bytes; add newline if Arduino expects it

# Optional: close the connection
arduino.close()
