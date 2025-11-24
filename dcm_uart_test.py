import time
import argparse
from DCM.core.serial_interface import SerialInterface

# Example params for testing the microcontroller firmware
# Example params for testing the microcontroller firmware
TEST_PARAMS = {
    # "MODE" is handled separately in send_parameters
    "ARP": 250,
    "VRP": 320,
    "atrial_amp": 3.0,
    "ventricular_amp": 3.5,
    "atrial_width": 5,          # Note: serial_interface casts to int. If this is ms, 5ms.
    "ventricular_width": 6,
    "atr_cmp_ref_pwm": 1200,
    "vent_cmp_ref_pwm": 1300,
    "reaction_time": 20,
    "recovery_time": 10,
    "PVARP": 200,
    "AV_delay": 150,            # FIXED_AV_DELAY -> AV_delay
    "response_factor": 8,
    "activity_threshold": 3,
    "URL": 150,                 # UPPER_RATE_LIMIT -> URL
    "LRL": 60,                  # LOWER_RATE_LIMIT -> LRL
    "MSR": 160,                 # MAXIMUM_SENSOR_RATE -> MSR
    "rate_smoothing": 5
}

TEST_MODE_ID = 3 # VVI

def on_ack():
    print("[MCU] ACK received")

def on_egram(ch, val):
    print(f"[MCU] EGRAM → ch={ch}, value={val}")

def main():
    parser = argparse.ArgumentParser(description="DCM UART test tool for Simulink team")
    parser.add_argument("port", help="Serial port connected to microcontroller")
    parser.add_argument("--baud", type=int, default=115200, help="UART baudrate")
    parser.add_argument("--send", action="store_true", help="Send parameter packet")
    parser.add_argument("--egram", action="store_true", help="Request EGRAM")
    
    args = parser.parse_args()

    iface = SerialInterface(args.port, args.baud)

    print(f"[INFO] Opening port {args.port} @ {args.baud} ...")
    iface.ack_callback = on_ack
    iface.egram_callback = on_egram
    iface.connect()

    time.sleep(0.5)

    if args.send:
        print("[INFO] Sending test parameters to microcontroller...")
        iface.send_parameters(TEST_PARAMS, mode_id_val=TEST_MODE_ID)

    if args.egram:
        print("[INFO] Requesting EGRAM data stream from microcontroller...")
        packet = iface._build_packet(0x02, b"")  # CMD_REQUEST_EGRAM
        iface.serial.write(packet)

    print("[INFO] Running. Press CTRL+C to exit.")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        iface.disconnect()


#to run first find the uart port thebn send params using
#python3 dcm_art_test.py /dev/tty.usbmodem1101 --send
#to check if ure sending data correctly
#python3 dcm_cli_uart_test.py /dev/tty.usbmodem1101 --egram

if __name__ == "__main__":
    main()