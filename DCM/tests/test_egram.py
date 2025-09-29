import pytest
from core import egram
import time 
def test_add_and_get_recent():
    buf = egram.EgramBuffer(maxlen=5)

    # add 3 samples
    buf.add_sample("atrial",0.1)
    buf.add_sample("atrial",0.2)
    buf.add_sample("atrial",0.4)
    
    recent = buf.get_recent("atrial",2)
    assert len(recent) ==2 
    assert [s.value for s in recent] == [0.2,0.4]

def test_buffer_overflow():
    buf = egram.EgramBuffer(maxlen=2)
    
    buf.add_sample("atrial",0.1)
    buf.add_sample("atrial",0.2)
    buf.add_sample("atrial",0.4)
    
    all_samples = buf.get_all("atrial")

    assert len(all_samples) ==2 
    assert [s.value for s in all_samples] == [0.2,0.4] # only the two newest values should remain

def test_get_all_and_clear():
    buf = egram.EgramBuffer(maxlen=5)

    buf.add_sample("surface",0.2)
    buf.add_sample("surface",0.4)
    
    all_samples = buf.get_all("surface")
    assert len(all_samples) ==2

    buf.clear()
    assert buf.get_all("surface") == []

def test_invalid_channel():
    buf = egram.EgramBuffer()

    with pytest.raises(ValueError) as e:
        buf.add_sample("invalid",1.0)
    assert "Not a Valid Chanel" in str(e.value)
    with pytest.raises(ValueError) as e:
        buf.get_recent("invalid",1)
