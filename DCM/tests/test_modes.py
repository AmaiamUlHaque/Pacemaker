import pytest
from core import modes

def test_parse_AOO(): #MOD-1
    info = modes.parse_mode(modes.PaceMakerMode.AOO)
    assert info.paced == "A"
    assert info.sensed == "O"
    assert info.response == "O"
    assert "Atrium paced" in info.descrpt
    assert "none sensed" in info.descrpt

def test_parse_VVI(): #MOD-2
    info = modes.parse_mode(modes.PaceMakerMode.VVI)
    assert info.paced == "V"
    assert info.sensed == "V"
    assert info.response == "I"
    assert "Ventricle paced" in info.descrpt
    assert "Inhibit" in info.descrpt

def test_list_modes_contains_all(): #MOD-3
    mode_dict = modes.list_modes()
    for mode in modes.PaceMakerMode:
        assert mode.value in mode_dict
        assert isinstance(mode_dict[mode.value],str)
        assert len(mode_dict[mode.value]) >0

def test_future_mode_extension(): #MOD-4
    
    info = modes.parse_mode("DOO") 
    assert info.paced == "D"
    assert info.sensed == "O"
    assert info.response == "O"
    assert "Dual paced" in info.descrpt
   


