import serial
import struct
import time 

PORT = 'COM3'  # Change as needed
BAUDRATE = 115200
TIMEOUT = 1  # seconds

ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
print(f"Opened serial port: {ser.name}")

def build_packet(fn_code,red, green,blue, off_time, switch_time):
    SYNC = 0x16
    packet = struct.pack('<BBBBBfH',   # Little endian: 1B+1B+1B+1B+1B+float(4B)+uint16(2B)
        SYNC,
        fn_code,
        red,
        green,
        blue,
        off_time,
        switch_time
    )
    return packet
try:
    for i in range(3):  # Send 3 example packets
        fn_code = 0x55            # Set parameters
        red_enable = i % 2        # Toggle red
        green_enable = (i + 1) % 2
        blue_enable = 0
        off_time = 1.5 + i        # seconds
        switch_time = 500 + i*100 # milliseconds

        packet = build_packet(fn_code, red_enable, green_enable, blue_enable, off_time, switch_time)
        ser.write(packet)

        print(f"Sent packet {i+1}: {packet.hex(' ')}")
        time.sleep(1)

finally:
    ser.close()
    print("\nSerial port closed.")