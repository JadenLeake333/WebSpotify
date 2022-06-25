# To Run tests run command "python -m pytest" in terminal

from application import helper_functions

def test_ms_time_conversion():
    assert helper_functions.ms_time_conversion(2277471) == "0h37m57s"
    assert helper_functions.ms_time_conversion(4891036) == "1h21m31s"
    assert helper_functions.ms_time_conversion(309338413) == "3d13h55m38s"

def test_pitch_class_conversion():
    assert helper_functions.pitch_class_conversion(3) == "D♯"
    assert helper_functions.pitch_class_conversion(5) == "F"
    assert helper_functions.pitch_class_conversion(0) == "C"

def test_check_error():
    assert helper_functions.check_error({"error":"Error"}) == True
    assert helper_functions.check_error({"not_error":"Error"}) == False
    assert helper_functions.check_error({"test":"test"}) == False

def test_pluraizer():
    assert helper_functions.pluraizer("test",True) == "tests"
    assert helper_functions.pluraizer("test",False) == "test"