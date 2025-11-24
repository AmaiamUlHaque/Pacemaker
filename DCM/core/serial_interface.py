import struct
import threading
import time
import serial 

START_BYTE = 0x16
END_BYTE = 0x04

CMD_SEND_PARAMS = 0x55
CMD_REQUEST_EGRAM = 0x22


class SerialInterface:
    def __init__(self, port, baudrate=115200):
        self.port_name = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        
        self.egram_callback = None
        self.ack_callback = None
    
    def connect(self):
        self.serial = serial.Serial(self.port_name, self.baudrate,timeout=0.1)
        self.running = True
        threading.Thread(target=self._read_loop, daemon=True).start()
    
    def disconnect(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            
    #build packet
    def _build_packet(self, cmd, payload_bytes):
        #length = len(payload_bytes)
        packet = bytearray()
        packet.append(START_BYTE)
        packet.append(cmd)
        packet.extend(payload_bytes)
        
        checksum = 0
        for b in packet[1:]:
            checksum ^= b
        packet.append(checksum)
        packet.append(END_BYTE)
        return packet

    #public api
    def send_parameters(self, params, mode_id_val=0):
        """
        params = Parameters object or dict containing keys matching params.py
        mode_id_val = Integer ID of the mode (from modes.py)
        """ 
        # Handle Parameters object
        if hasattr(params, 'to_dict'):
            p = params.to_dict()
        else:
            p = params

        # Helper to safely get value
        def get_val(key, default=0):
            return p.get(key, default)

        values = [
            mode_id_val,                            # MODE
            get_val("ARP"),                         # ARP
            get_val("VRP"),                         # VRP
            int(get_val("atrial_amp")  ),        # ATR_AMPLITUDE
            int(get_val("ventricular_amp") ),   # VENT_AMPLITUDE
            get_val("atrial_width"),                # ATR_PULSEWIDTH
            get_val("ventricular_width"),           # VENT_PULSEWIDTH
            get_val("atr_cmp_ref_pwm"),             # ATR_CMP_REF_PWM
            get_val("vent_cmp_ref_pwm"),            # VENT_CMP_REF_PWM
            get_val("reaction_time"),               # REACTION_TIME
            get_val("recovery_time"),               # RECOVERY_TIME
            get_val("PVARP"),                       # PVARP
            get_val("AV_delay"),                    # FIXED_AV_DELAY
            get_val("response_factor"),             # RESPONSE_FACTOR
            get_val("activity_threshold"),          # ACTIVITY_THRESHOLD
            get_val("LRL"),                         # LOWER_RATE_LIMIT
            get_val("URL"),                         # UPPER_RATE_LIMIT
            get_val("MSR"),                         # MAXIMUM_SENSOR_RATE
            get_val("rate_smoothing")               # RATE_SMOOTHING
        ]
        
     
        
        values = [int(v) if not isinstance(v, float) else int(v) for v in values]
     

        print(f"[DEBUG] Packing parameters: {values}")
        payload = struct.pack("<19H", *values)
        packet = self._build_packet(CMD_SEND_PARAMS,payload)
        print(f"[DEBUG] Sending Parameter Packet: {packet.hex()}")
        self.serial.write(packet)
    
    def _read_loop(self):
        buffer = bytearray()
        while self.running:
            try:
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    if data:
                        print(f"[DEBUG] RAW READ: {data.hex()}")
                        buffer.extend(data)
                        
                        while True:
                            # 1. Find START_BYTE
                            if not buffer:
                                break
                                
                            if buffer[0] != START_BYTE:
                                try:
                                    start_idx = buffer.index(START_BYTE)
                                    print(f"[DEBUG] Discarding garbage: {buffer[:start_idx].hex()}")
                                    del buffer[:start_idx]
                                except ValueError:
                                    # No start byte found yet, discard all
                                    print(f"[DEBUG] Discarding garbage: {buffer.hex()}")
                                    buffer.clear()
                                    break
                            
                            # 2. Check if we have enough for header (START, CMD)
                            if len(buffer) < 2:
                                break
                                
                            cmd = buffer[1]
                            
                            # Determine payload length based on command
                            # CMD_SEND_PARAMS: Not received by PC usually, but for completeness
                            # CMD_REQUEST_EGRAM: 0 payload
                            # ACK (0xAA): 0 payload
                            # EGRAM_DATA (0xE0): 3 bytes (1 byte ch + 2 bytes val)
                            
                            payload_len = 0
                            if cmd == 0xE0: # EGRAM DATA
                                payload_len = 3
                            elif cmd == 0xAA: # ACK
                                payload_len = 0
                            else:
                                # Unknown command or one we don't expect to receive with payload
                                # For robustness, if we don't know it, maybe we should just wait for more?
                                # But if it's garbage, we might get stuck. 
                                # Let's assume 0 for now or print warning
                                pass

                            total_len = 2 + payload_len + 2 # Header(2: START, CMD) + Payload(N) + Checksum(1) + End(1)
                            
                            # 3. Check if we have full packet
                            if len(buffer) < total_len:
                                break
                                
                            # 4. Extract packet
                            packet = buffer[:total_len]
                            del buffer[:total_len]
                            
                            self._process_packet(packet)
                            
            except Exception as e:
                print(f"[ERROR] Serial read error: {e}")
                time.sleep(1)
                
            time.sleep(0.001)
    
    def _process_packet(self,packet):
        print(f"[DEBUG] Processing packet: {packet.hex()}")
        if len(packet)<4:
            return
        if packet[0] != START_BYTE:
            return
        cmd = packet[1]
        # length is no longer in packet
        # payload is from index 2 up to -2 (excluding checksum and end)
        payload = packet[2:-2]
        recv_checksum = packet[-2]
        
        # Verify End Byte
        if packet[-1] != END_BYTE:
            print(f"[ERROR] Invalid End Byte: {hex(packet[-1])}")
            return

        calc_checksum = 0
        for b in packet[1:-2]: # CMD + PAYLOAD
            calc_checksum ^= b
        
        if recv_checksum != calc_checksum:
            print(f"[ERROR] Checksum mismatch! Recv: {hex(recv_checksum)}, Calc: {hex(calc_checksum)}")
            return
        
        if cmd == 0xAA:
            print("[DEBUG] Received ACK packet")
            if self.ack_callback:
                self.ack_callback()
        elif cmd == CMD_SEND_PARAMS:
            ack = self._build_packet(0xAA, b"")
            if self.serial:
                print(f"[DEBUG] Sending ACK: {ack.hex()}")
                self.serial.write(ack)
        elif cmd == 0xE0:
            if self.egram_callback:
                i = 0
                while i + 2 < len(payload):
                    ch = payload[i]
                    val = payload[i+1] | (payload[i+2] << 8)
                    self.egram_callback(ch, val)
                    i += 3
            
        
    