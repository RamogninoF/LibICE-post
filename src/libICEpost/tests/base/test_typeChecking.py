import pytest
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray, checkMap

def reset_globals():
    from libICEpost import GLOBALS
    GLOBALS.__SAFE_ITERABLE_CHECKING__ = True
    GLOBALS.__TYPE_CHECKING__ = True

def test_checkType_entryName_type_error():
    reset_globals()
    with pytest.raises(TypeError):
        checkType("test", str, entryName=123)

def test_checkType_intAsFloat_type_error():
    reset_globals()
    with pytest.raises(TypeError):
        checkType("test", str, intAsFloat="True")

def test_checkType_checkForNone_type_error():
    reset_globals()
    with pytest.raises(TypeError):
        checkType("test", str, checkForNone="False")

def test_checkType_Type_type_error():
    reset_globals()
    with pytest.raises(TypeError):
        checkType("test", 123)

def test_checkType_Type_iterable_type_error():
    reset_globals()
    with pytest.raises(TypeError):
        checkType("test", [str, 123])

def test_checkType_NoneType_no_check():
    reset_globals()
    checkType(None, type(None), checkForNone=False)

def test_checkType_intAsFloat():
    reset_globals()
    checkType(5, float, intAsFloat=True)

def test_checkArray_correct_type():
    reset_globals()
    checkArray([1, 2, 3], int)

def test_checkArray_incorrect_type():
    reset_globals()
    with pytest.raises(TypeError):
        checkArray([1, "2", 3], int)

def test_checkArray_empty():
    reset_globals()
    checkArray([], int)

def test_checkArray_safe_iterable_checking():
    reset_globals()
    from libICEpost import GLOBALS
    GLOBALS.__SAFE_ITERABLE_CHECKING__ = True
    with pytest.raises(TypeError):
        checkArray([1, "2", 3], int)
    reset_globals()
    GLOBALS.__SAFE_ITERABLE_CHECKING__ = False
    checkArray([1, "2", 3], int)
    reset_globals()

def test_checkMap_correct_type():
    reset_globals()
    checkMap({"a": 1, "b": 2}, str, int)

def test_checkMap_incorrect_key_type():
    reset_globals()
    with pytest.raises(TypeError):
        checkMap({1: 1, "b": 2}, str, int)

def test_checkMap_incorrect_value_type():
    reset_globals()
    with pytest.raises(TypeError):
        checkMap({"a": 1, "b": "2"}, str, int)

def test_checkMap_empty():
    reset_globals()
    checkMap({}, str, int)

def test_checkMap_safe_iterable_checking():
    reset_globals()
    from libICEpost import GLOBALS
    GLOBALS.__SAFE_ITERABLE_CHECKING__ = True
    with pytest.raises(TypeError):
        checkMap({"a": 1, "b": "2"}, str, int)
    reset_globals()
    GLOBALS.__SAFE_ITERABLE_CHECKING__ = False
    checkMap({"a": 1, "b": "2"}, str, int)
    reset_globals()

def test_checkType_correct_type():
    reset_globals()
    checkType("test", str)

def test_checkType_incorrect_type():
    reset_globals()
    with pytest.raises(TypeError):
        checkType(5, str)

def test_checkType_incorrect_type_with_entryName():
    reset_globals()
    with pytest.raises(TypeError):
        checkType(5, str, entryName="test_entry")

def test_checkType_iterable_type_correct():
    reset_globals()
    checkType(5, (int, float))

def test_checkType_iterable_type_incorrect():
    reset_globals()
    with pytest.raises(TypeError):
        checkType(5, (str, list))

def test_checkType_checkForNone_true():
    reset_globals()
    with pytest.raises(TypeError):
        checkType(5, type(None), checkForNone=True)