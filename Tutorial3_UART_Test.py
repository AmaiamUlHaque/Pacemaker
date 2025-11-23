'''
TO SEND PARAMS TO MCU:
1) find UART Port
2) in terminal: 
    python3 Tutorial3_UART_Test.py UART_Port --send
    Eg. 
    - python3 Tutorial3_UART_Test.py 'COM4' --send
    - python3 Tutorial3_UART_Test.py '/dev/tty.usbmodem1101' --send
'''

# USE CTRL+/ TO COMMENT/UNCOMMENT CODE SELECTED
# TRY USING OG CODE FIRST, IDK IF THE OTHER ONE BELOW IT WORKS
# tbh idk if either of them works, but the og one should work?


# OG CODE:

# import time
# import argparse
# from DCM.core.serial_interface import SerialInterface

# # params sent to microcontroller
# TEST_PARAMS = { # what is the data thats in place for bytes 0, 1, 2?
#                         # byte 0:2???
#     "red_enable": 1,    # byte 3     --> uint8 in 0/1
#     "green_enable": 1,  # byte 4     --> uint8 in 0/1
#     "blue_enable": 1,   # byte 5     --> uint8 in 0/1      
#     "off_time": 0.5,    # byte 6:9   --> single in s
#     "switch_time": 200, # byte 10:11 --> uint16 in ms
# }

# def on_ack():
#     print("[MCU] ACK received")

# def main():
#     parser = argparse.ArgumentParser(description="DCM UART test tool for Simulink team")
#     parser.add_argument("port", help="Serial port connected to microcontroller")
#     parser.add_argument("--baud", type=int, default=115200, help="UART baudrate")
#     parser.add_argument("--send", action="store_true", help="Send parameter packet")
    
#     args = parser.parse_args()

#     iface = SerialInterface(args.port, args.baud)

#     print(f"[INFO] Opening port {args.port} @ {args.baud} ...")
#     iface.ack_callback = on_ack
#     iface.connect()

#     time.sleep(0.5)

#     if args.send:
#         print("[INFO] Sending test parameters to microcontroller...")
#         iface.send_parameters(TEST_PARAMS)

#     print("[INFO] Running. Press CTRL+C to exit.")
    
#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\n[INFO] Exiting...")
#         iface.disconnect()

# if __name__ == "__main__":
#     main()








# NOT OG CODE: BETTER FOR DISPLAYING REAL TIME VALUES (COURTESY OF CHATGPT)

# import time
# import argparse
# from DCM.core.serial_interface import SerialInterface

# # params sent to microcontroller
# TEST_PARAMS = { # what is the data thats in place for bytes 0, 1, 2?
#                         # byte 0:2???
#     "red_enable": 1,    # byte 3     --> uint8 in 0/1
#     "green_enable": 1,  # byte 4     --> uint8 in 0/1
#     "blue_enable": 1,   # byte 5     --> uint8 in 0/1      
#     "off_time": 0.5,    # byte 6:9   --> single in s
#     "switch_time": 200, # byte 10:11 --> uint16 in ms
# }

# # Global variable to track program start time
# start_time = time.time()

# def on_ack():
#     print("[MCU] ACK received")

# def display_outgoing_data(data_bytes):
#     """Display outgoing byte data in the requested format"""
#     current_time = time.time()
#     time_since_start = current_time - start_time
    
#     print("\n" + "="*50)
#     print("OUTGOING DATA TO MCU:")
#     print(f"Time: timestamp in s: {time_since_start:.3f}, current time: {time.strftime('%H:%M:%S')}")
    
#     # Display individual bytes
#     for i, byte_val in enumerate(data_bytes):
#         if i == 0:
#             print(f"Byte {i} = ??? = {byte_val}")
#         elif i == 1:
#             print(f"Byte {i} = ??? = {byte_val}")
#         elif i == 2:
#             print(f"Byte {i} = ??? = {byte_val}")
#         elif i == 3:
#             print(f"Byte {i} = red_enable = {byte_val}")
#         elif i == 4:
#             print(f"Byte {i} = green_enable = {byte_val}")
#         elif i == 5:
#             print(f"Byte {i} = blue_enable = {byte_val}")
    
#     # Display byte ranges for multi-byte values
#     if len(data_bytes) >= 10:
#         off_time_bytes = data_bytes[6:10]
#         switch_time_bytes = data_bytes[10:12] if len(data_bytes) >= 12 else data_bytes[10:]
        
#         print(f"Byte 6:9 = off_time = {list(off_time_bytes)}")
#         print(f"Byte 10:11 = switch_time = {list(switch_time_bytes)}")
    
#     print("="*50)

# def send_parameters_with_display(iface, params):
#     """Wrapper function to send parameters and display the byte data"""
#     # Convert parameters to bytes (you'll need to adapt this based on your SerialInterface implementation)
#     # This is a simplified version - you may need to modify based on how send_parameters actually works
    
#     print("[INFO] Sending test parameters to microcontroller...")
    
#     # Call the original send_parameters method
#     iface.send_parameters(params)
    
#     # Since we can't easily intercept the bytes from send_parameters,
#     # we'll create the byte representation manually for display
#     # You'll need to adjust this based on your actual data format
    
#     # Example byte construction (adjust according to your protocol):
#     data_bytes = [
#         0,  # byte 0 - placeholder
#         0,  # byte 1 - placeholder  
#         0,  # byte 2 - placeholder
#         params["red_enable"],     # byte 3
#         params["green_enable"],   # byte 4
#         params["blue_enable"],    # byte 5
#     ]
    
#     # Convert off_time (float) to 4 bytes
#     off_time_bytes = list(int(params["off_time"] * 1000).to_bytes(4, byteorder='little'))
#     data_bytes.extend(off_time_bytes)
    
#     # Convert switch_time (int) to 2 bytes
#     switch_time_bytes = list(params["switch_time"].to_bytes(2, byteorder='little'))
#     data_bytes.extend(switch_time_bytes)
    
#     # Display the outgoing data
#     display_outgoing_data(data_bytes)

# def main():
#     parser = argparse.ArgumentParser(description="DCM UART test tool for Simulink team")
#     parser.add_argument("port", help="Serial port connected to microcontroller")
#     parser.add_argument("--baud", type=int, default=115200, help="UART baudrate")
#     parser.add_argument("--send", action="store_true", help="Send parameter packet")
    
#     args = parser.parse_args()

#     iface = SerialInterface(args.port, args.baud)

#     print(f"[INFO] Opening port {args.port} @ {args.baud} ...")
#     iface.ack_callback = on_ack
#     iface.connect()

#     time.sleep(0.5)

#     if args.send:
#         # Use our wrapper function instead of direct send_parameters
#         send_parameters_with_display(iface, TEST_PARAMS)

#     print("[INFO] Running. Press CTRL+C to exit.")
    
#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\n[INFO] Exiting...")
#         iface.disconnect()

# if __name__ == "__main__":
#     main()