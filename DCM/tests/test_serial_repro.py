import sys
import os
import struct
import unittest
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from DCM.core.serial_interface import SerialInterface, CMD_SEND_PARAMS
from DCM.core.params import Parameters
from DCM.core.modes import PaceMakerMode, mode_id

class TestSerialInterface(unittest.TestCase):
    def setUp(self):
        self.serial_interface = SerialInterface("TEST_PORT")
        self.serial_interface.serial = MagicMock()
        
        # Create a sample Parameters object
        self.params = Parameters(
            LRL=60, URL=120, MSR=120, rate_smoothing=0,
            atrial_amp=3.5, atrial_width=0.4, atrial_sensitivity=0.75, ARP=250,
            ventricular_amp=3.5, ventricular_width=0.4, ventricular_sensitivity=0.75, VRP=320,
            PVARP=250, AV_delay=150,
            activity_threshold=3, reaction_time=30, recovery_time=5, response_factor=8,
            atr_cmp_ref_pwm=50, vent_cmp_ref_pwm=50
        )
        self.mode = PaceMakerMode.VVI

    def test_send_parameters_packing(self):
        # Now we test that it works with the Parameters object and separate mode_id
        
        try:
            # Pass the Parameters object directly and the mode ID
            self.serial_interface.send_parameters(self.params, mode_id(self.mode))
        except KeyError as e:
            self.fail(f"send_parameters raised KeyError unexpectedly: {e}")
        except Exception as e:
            self.fail(f"send_parameters raised exception: {e}")

        # Verify that write was called
        self.serial_interface.serial.write.assert_called_once()
        
        # We could also inspect the call args to verify the packet content if needed
        # args, _ = self.serial_interface.serial.write.call_args
        # packet = args[0]
        # print(f"Sent packet: {packet.hex()}")

if __name__ == '__main__':
    unittest.main()
