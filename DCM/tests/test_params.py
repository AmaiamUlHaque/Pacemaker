import os
import pytest
from core import params

TEST_FILE = os.path.join(os.path.dirname(__file__),"test_params.json")
params.PARAMS_FILE = TEST_FILE

@pytest.fixture(autouse=True)
def cleanup():
    """ensure a clean slate before each test"""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_valid_save_and_load():
    p = params.Parameters(
        LRL=60,
        URL=120,
        atrial_amp=3.5,
        atrial_width=0.5,
        ventricular_amp=3.5,
        ventricular_width=0.5,
        VRP=250,
        ARP=250,
    )
    #all params valid 
    assert p.validate() is True
    
    params.save_parameters(p)
    loaded = params.load_parameters()
    assert loaded == p
    
def test_invalid_LRL():
    p = params.Parameters(
        LRL=20, #too low
        URL=120,
        atrial_amp=3.5,
        atrial_width=0.5,
        ventricular_amp=3.5,
        ventricular_width=0.5,
        VRP=250,
        ARP=250,
    )
    with pytest.raises(ValueError):
        p.validate()

def test_URL_higher_than_LRL():
    p = params.Parameters(
        LRL=100,
        URL=90,
        atrial_amp=3.5,
        atrial_width=0.5,
        ventricular_amp=3.5,
        ventricular_width=0.5,
        VRP=250,
        ARP=250,
    )
    with pytest.raises(ValueError):
        p.validate()

def test_invalid_amp():
    p = params.Parameters(
        LRL=60,
        URL=120,
        atrial_amp=10.0, #too high
        atrial_width=0.5,
        ventricular_amp=3.5,
        ventricular_width=0.5,
        VRP=250,
        ARP=250,
    )
    with pytest.raises(ValueError):
        p.validate()