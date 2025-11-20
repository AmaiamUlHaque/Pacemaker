from typing import Dict
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class ModeInfo:
    paced: str
    sensed: str
    response: str
    rate: bool          # Deliverable 2: R = rate modulation
    descrpt: str

class PaceMakerMode(Enum):
    AOO  = "AOO"
    VOO  = "VOO"
    AAI  = "AAI"
    VVI  = "VVI"
    AOOR = "AOOR"
    VOOR = "VOOR"
    AAIR = "AAIR"
    VVIR = "VVIR"
    DDDR = "DDDR"

MODE_ID_MAP = {
    "AOO": 0,
    "VOO": 1,
    "AAI": 2,
    "VVI": 3,
    "AOOR": 4,
    "VOOR": 5,
    "AAIR": 6,
    "VVIR": 7,
    "DDDR": 8
}

def parse_mode(mode) -> ModeInfo:
    """Parse the mode string or enum into ModeInfo."""
    if isinstance(mode, PaceMakerMode):
        code = mode.value
    else:
        code = str(mode).upper()

    # Extract rate response (R)
    rate = code.endswith("R")
    if rate:
        code = code[:-1]

    if len(code) < 3:
        code = code.ljust(3, "O")

    paced, sensed, response = code[0], code[1], code[2]

    desc_map = {
        "O": "none",
        "A": "Atrium",
        "V": "Ventricle",
        "D": "Dual",
        "I": "Inhibit",
        "T": "Trigger",
    }

    descrpt = (
        f"{code}{'R' if rate else ''}: "
        f"{desc_map.get(paced, paced)} paced, "
        f"{desc_map.get(sensed, sensed)} sensed, "
        f"{desc_map.get(response, response)} response, "
        f"{'Rate-responsive ON' if rate else 'No rate response'}"
    )

    return ModeInfo(
        paced=paced,
        sensed=sensed,
        response=response,
        rate=rate,
        descrpt=descrpt
    )

def list_modes() -> Dict[str, str]:
    """Return mode -> description for all supported modes."""
    return {mode.value: parse_mode(mode).descrpt for mode in PaceMakerMode}

def mode_id(mode) -> int:
    """Return numeric ID used by the Simulink hardware."""
    if isinstance(mode, PaceMakerMode):
        key = mode.value
    else:
        key = str(mode).upper()
    return MODE_ID_MAP[key]
