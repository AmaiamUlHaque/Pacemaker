import sys
import os
import struct
from unittest.mock import MagicMock

# Mock serial module BEFORE importing serial_interface
sys.modules["serial"] = MagicMock()

sys.path.append(os.getcwd())
from DCM.core.serial_interface import SerialInterface, CMD_SEND_PARAMS, CMD_REQUEST_EGRAM

def test_new_protocol():
    print("Testing New Serial Protocol...")
    iface = SerialInterface("test_port")
    iface.serial = MagicMock()
    
    # 1. Test Send Parameters
    # Expected: [CMD_SEND_PARAMS, PAYLOAD..., CHECKSUM, END]
    params = {
        "ARP": 250, "VRP": 320, "atrial_amp": 3.0, "ventricular_amp": 3.5,
        "atrial_width": 5, "ventricular_width": 6, "atr_cmp_ref_pwm": 1200,
        "vent_cmp_ref_pwm": 1300, "reaction_time": 20, "recovery_time": 10,
        "PVARP": 200, "AV_delay": 150, "response_factor": 8,
        "activity_threshold": 3, "URL": 150, "LRL": 60, "MSR": 160,
        "rate_smoothing": 5
    }
    
    iface.send_parameters(params, mode_id_val=3)
    
    args, _ = iface.serial.write.call_args
    packet = args[0]
    
    print(f"\n[Send Params] Packet: {packet.hex()}")
    
    # Validation
    # Packet structure: [START, CMD, PAYLOAD..., CHECKSUM, END]
    start_byte = packet[0]
    cmd = packet[1]
    # payload is from index 2 up to -2 (excluding checksum and end)
    payload = packet[2:-2]
    checksum = packet[-2]
    end = packet[-1]
    
    print(f"START: {hex(start_byte)} (Expected 0x16)")
    print(f"CMD: {hex(cmd)} (Expected {hex(CMD_SEND_PARAMS)})")
    print(f"Payload Len: {len(payload)} (Expected 38 for 19 shorts)")
    print(f"END: {hex(end)} (Expected 0x04)")
    
    if cmd != CMD_SEND_PARAMS:
        print("FAIL: Wrong Command Byte")
        return
    if len(payload) != 38:
        print("FAIL: Wrong Payload Length")
        return
    
    # Checksum verification
    calc_checksum = 0
    calc_checksum = 0
    for b in packet[1:-2]: # CMD + PAYLOAD (Exclude START, CHECKSUM, END)
        calc_checksum ^= b
        
    if checksum != calc_checksum:
        print(f"FAIL: Checksum mismatch. Calc: {hex(calc_checksum)}, Pkt: {hex(checksum)}")
    else:
        print("PASS: Checksum correct")

    # 2. Test Request EGRAM
    # Expected: [CMD_REQUEST_EGRAM, CHECKSUM, END]
    print("\n[Request EGRAM]")
    packet = iface._build_packet(CMD_REQUEST_EGRAM, b"")
    print(f"Packet: {packet.hex()}")
    
    if packet[1] != CMD_REQUEST_EGRAM:
        print("FAIL: Wrong CMD")
    
    # 3. Test Receive Processing (ACK)
    # Packet: [START, 0xAA, CHECKSUM, END]
    # START=0x16, CMD=0xAA, CS=0xAA (CMD only), END=0x04
    print("\n[Receive ACK]")
    # Checksum = 0xAA
    ack_packet = bytearray([0x16, 0xAA, 0xAA, 0x04])
    
    ack_called = False
    def on_ack():
        nonlocal ack_called
        ack_called = True
        print("Callback: ACK Received")
        
    iface.ack_callback = on_ack
    iface._process_packet(ack_packet)
    
    if ack_called:
        print("PASS: ACK Callback triggered")
    else:
        print("FAIL: ACK Callback NOT triggered")

if __name__ == "__main__":
    test_new_protocol()
