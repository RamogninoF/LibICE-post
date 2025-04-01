import pytest
import numpy as np
from libICEpost.src.base.filters._Clone import Clone

def test_clone_initialization():
    # Test that the Clone filter initializes correctly
    clone_filter = Clone()
    assert isinstance(clone_filter, Clone)

def test_clone_call():
    # Test the __call__ method of the Clone filter
    clone_filter = Clone()
    xp = [1, 2, 3]
    yp = [4, 5, 6]
    
    xp_out, yp_out = clone_filter(xp, yp)
    
    assert isinstance(xp_out, np.ndarray)
    assert isinstance(yp_out, np.ndarray)
    assert np.array_equal(xp_out, np.array(xp))
    assert np.array_equal(yp_out, np.array(yp))

def test_clone_fromDictionary():
    # Test the fromDictionary method of the Clone filter
    clone_filter = Clone.fromDictionary({})
    assert isinstance(clone_filter, Clone)
