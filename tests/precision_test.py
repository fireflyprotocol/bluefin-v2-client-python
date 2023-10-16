import unittest
import json
import os
import sys
import pytest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))
sys.path.insert(1, os.path.join(os.getcwd(), "tests"))


from bluefin_v2_client.utilities import *
def test_precision_base18():
    assert (str(to_base18(0.05123234))=="51232340000000000") 
    
    
def test_precision_frombase18():
    assert str(from1e18(51232340000000000))=="0.05123234"


def test_precision_base6():
    assert (str(toUsdcBase(0.512323))=="512323")
    
    
def test_precision_frombase6():
    assert str(fromUsdcBase(512323))=="0.512323"
    
def test_precision_basesui():
    assert str(toSuiBase("0.23423001"))=="234230010"


def test_precision_frombasesui():
    assert str(fromSuiBase(234230010))=="0.23423001"