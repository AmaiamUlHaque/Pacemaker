from collections import deque
from dataclasses import dataclass 
from typing import Dict, List, Deque 
import time 

CHANNEL_MAP = {
    0: "atrial",
    1: "ventricular"
}
@dataclass
class EgramSample:
    timestamp:float
    channel:str
    value:float


class EgramBuffer:
    """
    This class buffers the egram data and splits it by channel.
    Keeps only the N most recent values per channel.
    """
    def __init__(self, maxlen: int=1000):
        self.buffers: Dict[str, Deque[EgramSample]] = {
            "atrial": deque(maxlen=maxlen),
            "ventricular": deque(maxlen=maxlen),
        }

    def add_sample(self, channel:str | int, value: int, timestamp : float = None  ) -> None:
        if isinstance(channel,int):
            if channel not in CHANNEL_MAP:
                raise ValueError(f"Not a Valid Chanel")
            channel = CHANNEL_MAP[channel]
        if channel not in self.buffers:
            raise ValueError(f"Invalid Channel")
        if timestamp is None:
            timestamp = time.time()
        sample = EgramSample(timestamp=timestamp, channel=channel, value=value)
        self.buffers[channel].append(sample)

    def add_samples(self, samples: List[tuple]):
        for ch, val, ts in samples:
            self.add_sample(ch,val,ts)
    
    def get_recent(self, channel:str, n:int) -> List[EgramSample]:
        if channel not in self.buffers:
            raise ValueError(f"{channel} is Not a Valid Chanel")
        
        return list(self.buffers[channel])[-n:]
    
    def get_all(self, channel:str) -> List[EgramSample]:
        if channel not in self.buffers:
            raise ValueError(f"{channel} is Not a Valid Chanel")
        return list(self.buffers[channel])


    def clear(self)-> None:
        for ch in self.buffers:
            self.buffers[ch].clear()

        


