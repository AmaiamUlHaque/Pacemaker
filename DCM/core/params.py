import json
from typing import Dict, Any
from dataclasses import dataclass, asdict
import os

PARAMS_FILE = os.path.join(os.path.dirname(__file__), "..","storage", "params.json")

@dataclass
class Parameters():
    #Core Programmable Parameters (Only For Deliverable 1)
    LRL :int                              #lower rate limit (ppm)
    URL :int                              #upper rate limit (ppm)
    atrial_amp :float                     #atrial amplitude (V)
    atrial_width :float                   #atrial width (ms)
    ventricular_amp :float                #Ventricular Amplitude (V)
    ventricular_width :float              #Ventricular Width (ms)
    VRP :int                              #Ventricular Refractory Period (ms)
    ARP :int                              #Atrial Refractory Period (ms)
    
    def validate(self) -> bool:
        """This function makes sure that the parameters are in the valid range as defined in appendix A"""
        
        if not(30 <= self.LRL <= 175):
            raise ValueError(f"LRL {self.LRL} out of range (30-175ppm)")
        if not(50 <= self.URL <=175):
            raise ValueError(f"URL {self.URL} out of range (50-175ppm)")
        if (self.LRL >= self.URL):
            raise ValueError(f"URL must be greater than LRL")
        
        #no clue if the amplitudes are in regulated or unregulated mode might need to change upper lim
        if not (0.1 <= self.atrial_amp <= 5):
            raise ValueError(f"Atrial Amplitude {self.atrial_amp} out of range (0.1-5.0 V) ")
        if not (0.1 <= self.atrial_width <= 1.9):
            raise ValueError(f"Atrial Pulse Width {self.atrial_width} out of range (0.1-1.9 ms)")
        
        if not (0.1 <= self.ventricular_amp <= 5):
            raise ValueError(f"Ventricular Amplitude {self.atrial_amp} out of range (0.1-5.0 V) ")
        if not (0.1 <= self.ventricular_width <= 1.9):
            raise ValueError(f"Ventricular Pulse Width {self.atrial_width} out of range (0.1-1.9 ms)")
        
        if not (150 <= self.VRP <= 500):
            raise ValueError(f"VRP {self.VRP} out of range (150-500 ms)")
        if not (150 <= self.ARP <= 500):
            raise ValueError(f"ARP {self.VRP} out of range (150-500 ms)")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        "convert class to dictionary"
        return asdict(self)

#-----Persistence Helpers------ 
def save_parameters(params : Parameters) -> None:
        """Save Params to JSON File"""
        params.validate()
        with open(PARAMS_FILE, "w") as f:
            json.dump(params.to_dict(),f,indent=4)

def load_parameters() -> Parameters:
    """Load parameters from JSON into an object of the class above"""
    if not os.path.exists(PARAMS_FILE):
        raise FileNotFoundError("No parameters file found")
    with open(PARAMS_FILE, "r") as f:
        data = json.load(f)
    return Parameters(**data)

def reset_parameters_file() -> None:
    with open(PARAMS_FILE, "w") as f:
        json.dump({}, f,indent=4)
