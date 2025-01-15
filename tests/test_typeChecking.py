import pytest
import numpy as np
from src.libICEpost.src.base.Functions.typeChecking import checkType

def test_checkType_entryName_type_error():
    with pytest.raises(TypeError):
        checkType("test", str, entryName=123)

def test_checkType_intAsFloat_type_error():
    with pytest.raises(TypeError):
        checkType("test", str, intAsFloat="True")

def test_checkType_checkForNone_type_error():
    with pytest.raises(TypeError):
        checkType("test", str, checkForNone="False")

def test_checkType_Type_type_error():
    with pytest.raises(TypeError):
        checkType("test", 123)

def test_checkType_Type_iterable_type_error():
    with pytest.raises(TypeError):
        checkType("test", [str, 123])

def test_checkType_NoneType_no_check():
    checkType(None, type(None), checkForNone=False)

def test_checkType_intAsFloat():
    checkType(5, float, intAsFloat=True)

def test_checkType_correct_type():
    checkType("test", str)

def test_checkType_incorrect_type():
    with pytest.raises(TypeError):
        checkType(5, str)

def test_checkType_incorrect_type_with_entryName():
    with pytest.raises(TypeError):
        checkType(5, str, entryName="test_entry")

def test_checkType_iterable_type_correct():
    checkType(5, (int, float))

def test_checkType_iterable_type_incorrect():
    with pytest.raises(TypeError):
        checkType(5, (str, list))

def test_checkType_checkForNone_true():
    with pytest.raises(TypeError):
        checkType(5, type(None), checkForNone=True)