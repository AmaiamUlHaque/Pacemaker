import json
from typing import Dict, Any
from dataclasses import dataclass, asdict
import os

PARAMS_FILE = os.path.join(os.path.dirname(__file__), "..", "storage", "params.json")

@dataclass
class Parameters:

    # Basic rate parameters
    LRL: int
    URL: int
    MSR: int                # Maximum Sensor Rate
    rate_smoothing: int

    # Atrial parameters
    atrial_amp: float
    atrial_width: int       # 1–30 ms
    atrial_sensitivity: float
    ARP: int                # refractory

    # Ventricular parameters
    ventricular_amp: float
    ventricular_width: int  # 1–30 ms
    ventricular_sensitivity: float
    VRP: int

    # Timing parameters
    PVARP: int
    AV_delay: int

    # Rate response parameters
    activity_threshold: int
    reaction_time: int
    recovery_time: int
    response_factor: int

    # CMP Reference PWM
    atr_cmp_ref_pwm: int
    vent_cmp_ref_pwm: int

    def validate(self) -> bool:

        # Basic ranges
        if not (30 <= self.LRL <= 175):
            raise ValueError("LRL out of range (30–175)")
        if not (50 <= self.URL <= 175):
            raise ValueError("URL out of range (50–175)")
        if self.LRL >= self.URL:
            raise ValueError("URL must be greater than LRL")

        if not (self.URL <= self.MSR <= 175):
            raise ValueError("MSR must be >= URL and ≤ 175")

        if not (0 <= self.rate_smoothing <= 25):
            raise ValueError("Rate smoothing out of range")

        # Amplitude (0.1 – 5.0 V)
        for amp in (self.atrial_amp, self.ventrical_amp if hasattr(self, "ventrical_amp") else self.ventricular_amp):
            if not (0.1 <= amp <= 5.0):
                raise ValueError("Amplitude out of range (0.1–5.0 V)")

        # Sensitivity (0.0 – 5.0 V)
        for sens in (self.atrial_sensitivity, self.ventricular_sensitivity):
            if not (0.0 <= sens <= 5.0):
                raise ValueError("Sensitivity out of range (0–5.0 V)")

        # Pulse widths (1–30 ms)
        if not (1 <= self.atrial_width <= 30):
            raise ValueError("Atrial pulse width out of range (1–30 ms)")
        if not (1 <= self.ventricular_width <= 30):
            raise ValueError("Ventricular pulse width out of range (1–30 ms)")

        # Refractory periods
        for rp in (self.ARP, self.VRP):
            if not (150 <= rp <= 500):
                raise ValueError("ARP/VRP out of range (150–500 ms)")

        # PVARP
        if not (150 <= self.PVARP <= 500):
            raise ValueError("PVARP out of range")

        # AV delay
        if not (30 <= self.AV_delay <= 300):
            raise ValueError("AV delay out of range")

        # Rate response parameters
        if not (1 <= self.activity_threshold <= 7):
            raise ValueError("Activity threshold out of range (1–7)")
        if not (10 <= self.reaction_time <= 50):
            raise ValueError("Reaction time out of range (10–50 s)")
        if not (2 <= self.recovery_time <= 16):
            raise ValueError("Recovery time out of range (2–16 min)")
        if not (1 <= self.response_factor <= 16):
            raise ValueError("Response factor out of range (1–16)")

        return True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def save_parameters(params: Parameters) -> None:
    params.validate()
    with open(PARAMS_FILE, "w") as f:
        json.dump(params.to_dict(), f, indent=4)

def load_parameters() -> Parameters:
    if not os.path.exists(PARAMS_FILE):
        raise FileNotFoundError("No parameters file found")
    with open(PARAMS_FILE, "r") as f:
        data = json.load(f)
    return Parameters(**data)

def reset_parameters_file() -> None:
    with open(PARAMS_FILE, "w") as f:
        json.dump({}, f, indent=4)
