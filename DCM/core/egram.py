from collections import deque
from dataclasses import dataclass 
from typing import Dict, List, Deque 
import time 

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
            "surface":deque(maxlen=maxlen)
        }

    def add_sample(self, channel:str, value:float, timestamp : float = None  ) -> None:
        if channel not in self.buffers:
            raise ValueError(f"Not a Valid Chanel")
        if timestamp is None:
            timestamp = time.time()
        sample = EgramSample(timestamp=timestamp, channel=channel, value=value)
        self.buffers[channel].append(sample)

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

        


