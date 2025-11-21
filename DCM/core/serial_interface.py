import struct
import threading
import time
import serial 

START_BYTE = 0x16
END_BYTE = 0x04

CMD_SEND_PARAMS = 0x16
CMD_REQUEST_EGRAM = 0x02


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
        length = len(payload_bytes)
        packet = bytearray()
        packet.append(START_BYTE)
        packet.append(cmd)
        packet.append(length)
        packet.extend(payload_bytes)
        
        checksum = 0
        for b in packet[1:]:
            checksum ^= b
        packet.append(checksum)
        packet.append(END_BYTE)
        return packet

    #public api
    def send_parameters(self,params):
        """
        params = dict containing 19 keys matching the simulink model
        """ 
        values = [
            params["MODE"],
            params["ARP"],
            params["VRP"],
            int(params["ATR_AMPLITUDE"]*10),
            int(params["VENT_AMPLITUDE"]*10),
            params["ATR_PULSEWIDTH"],
            params["VENT_PULSEWIDTH"],
            params["ATR_CMP_REF_PWM"],
            params["VENT_CMP_REF_PWM"],
            params["REACTION_TIME"],
            params["RECOVERY_TIME"],
            params["PVARP"],
            params["FIXED_AV_DELAY"],
            params["RESPONSE_FACTOR"],
            params["ACTIVITY_THRESHOLD"],
            params["UPPER_RATE_LIMIT"],
            params["LOWER_RATE_LIMIT"],
            params["MAXIMUM_SENSOR_RATE"],
            params["RATE_SMOOTHING"]
        ]
        payload = struct.pack("<19H", *values)
        packet = self._build_packet(CMD_SEND_PARAMS,payload)
        self.serial.write(packet)
    
    def _read_loop(self):
        buffer = bytearray()
        while self.running:
            if self.serial.in_waiting:
                byte = self.serial.read(1)
                if byte:
                    buffer.extend(byte)
                    if END_BYTE in buffer:
                        packet, _, remainder = buffer.partition(bytes([END_BYTE]))
                        packet += bytes([END_BYTE])
                        buffer = remainder
                        self._process_packet(packet)
            time.sleep(0.001)
    
    def _process_packet(self,packet):
        if len(packet)<5:
            return
        if packet[0] != START_BYTE:
            return
        cmd = packet[1]
        length = packet[2]
        payload = packet[3: 3+ length]
        recv_checksum = packet[3+length]
        if len(packet) < 5 + length:
            print("PACKET LENGTH MISMATCH")
            return
        calc_checksum = 0
        
        for b in packet[1:3+length]:
            calc_checksum ^= b
        
        if recv_checksum != calc_checksum:
            print("CHECKSUM ERROR")
            return
        
        if cmd == 0xAA:
            if self.ack_callback:
                self.ack_callback()
        elif cmd == CMD_SEND_PARAMS:
            ack = self._build_packet(0xAA, b"")
            if self.serial:
                self.serial.write(ack)
        elif cmd == 0xE0:
            if self.egram_callback:
                i = 0
                while i + 2 < len(payload):
                    ch = payload[i]
                    val = payload[i+1] | (payload[i+2] << 8)
                    self.egram_callback(ch, val)
                    i += 3
            
        
    