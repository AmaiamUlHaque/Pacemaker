from typing import Dict
from dataclasses import dataclass
from enum import Enum
@dataclass(frozen=True)
class ModeInfo:
    paced:str
    sensed:str
    response:str
    descrpt:str

class PaceMakerMode(Enum):
    AOO = "AOO"
    VOO = "VOO"  
    AAI = "AAI" 
    VVI = "VVI" 


def parse_mode(mode: PaceMakerMode) -> ModeInfo:
    """Parse the three letter mode string into mode info"""
    if isinstance(mode, PaceMakerMode):
        code = mode.value
    elif isinstance(mode,str):
        code = mode
    else:
        try:
            code = str(mode.value)
        except Exception:
            raise TypeError("mode must be a PaceMakerMode or a 3-letter mode str")
    code = code.upper()
    if len(code) < 3:
        code = code.ljust(3,"O")
    paced, sensed, response = code[0], code[1], code[2]

    desc_map={
        "O": "none",
        "A": "Atrium",
        "V": "Ventricle",
        "D": "Dual",
        "I": "Inhibit",
        "T": "Trigger",
    }



    descrpt = f"{code}: {desc_map.get(paced,paced)} paced, "\
              f"{desc_map.get(sensed,sensed)} sensed, " \
              f"{desc_map.get(response, response)} response"

    return ModeInfo(paced=paced, sensed=sensed, response=response, descrpt= descrpt)

def list_modes():
    """Return a dict of mode"""
    return {mode.value: parse_mode(mode).descrpt for mode in PaceMakerMode}









    
    
    





