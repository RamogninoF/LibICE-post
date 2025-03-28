from libICEpost.src.base.enum import Enum
import traceback
import pytest

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def test_enum_valid_value():
    assert Color(1) == Color.RED
    assert Color(2) == Color.GREEN
    assert Color(3) == Color.BLUE

def test_enum_invalid_value():
    with pytest.raises(ValueError) as excinfo:
        Color(4)
    assert f"Allowed {Color.__name__}s are:" in "\n".join(traceback.format_exception(excinfo.value))
    assert "RED" in "\n".join(traceback.format_exception(excinfo.value))
    assert "GREEN" in "\n".join(traceback.format_exception(excinfo.value))
    assert "BLUE" in "\n".join(traceback.format_exception(excinfo.value))
