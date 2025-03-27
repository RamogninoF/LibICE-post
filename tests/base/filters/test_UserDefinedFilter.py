import pytest
import numpy as np
from libICEpost.src.base.filters._UserDefinedFilter import UserDefinedFilter

def test_user_defined_filter_initialization():
    # Define a sample filter function
    def sample_filter(x, y):
        return x[::2], y[::2]
    
    # Initialize the UserDefinedFilter
    udf = UserDefinedFilter(sample_filter)
    
    # Assert the function is correctly set
    assert udf.function == sample_filter

def test_user_defined_filter_call():
    # Define a sample filter function
    def sample_filter(x, y):
        return x[::2], y[::2]
    
    # Initialize the UserDefinedFilter
    udf = UserDefinedFilter(sample_filter)
    
    # Define sample input data
    x = np.linspace(0, 10, 11)
    y = np.linspace(10, 20, 11)
    
    # Apply the filter
    x_filtered, y_filtered = udf(x, y)
    
    # Assert the filtered data is correct
    assert np.array_equal(x_filtered, x[::2])
    assert np.array_equal(y_filtered, y[::2])

def test_user_defined_filter_invalid_function():
    # Define an invalid filter function
    def invalid_filter(x):
        return x
    
    # Assert that initializing with an invalid function raises an error
    with pytest.raises(ValueError):
        UserDefinedFilter(invalid_filter)

def test_user_defined_filter_from_dictionary():
    # Define a sample filter function
    def sample_filter(x, y):
        return x[::2], y[::2]
    
    # Create a dictionary with the function
    dictionary = {"function": sample_filter}
    
    # Create the UserDefinedFilter from the dictionary
    udf = UserDefinedFilter.fromDictionary(dictionary)
    
    # Assert the function is correctly set
    assert udf.function == sample_filter
