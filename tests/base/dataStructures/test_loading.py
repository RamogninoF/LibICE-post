import pytest
from libICEpost.src.base.dataStructures._loading import (
    load_file, load_array, load_uniform, load_function, load_calculated, loadField, LoadingMethod
)
from libICEpost.src.base.dataStructures._TimeSeries import TimeSeries
import tempfile

@pytest.fixture
def timeseries():
    # A time series object to be used in tests
    ts = TimeSeries()
    return ts

def test_load_file(timeseries):
    with tempfile.NamedTemporaryFile(delete=True, mode="w") as temp_file:
        temp_file.write("1 2\n3 4\n5 6\n")
        temp_file.flush()
        temp_file_path = temp_file.name
        
        fieldName = "new_field"
        load_file(timeseries, filename=temp_file_path, field=fieldName, verbose=True)
        assert fieldName in timeseries.columns
        assert timeseries[fieldName].to_list() == [2, 4, 6]
        assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
        assert timeseries.timeName in timeseries.columns

def test_load_array(timeseries):
    data = [[1, 2], [3, 4], [5, 6]]
    fieldName = "new_field"
    load_array(timeseries, array=data, field=fieldName, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [2, 4, 6]
    assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
    assert timeseries.timeName in timeseries.columns
    
    data2 = [[1, 5, 10], [9, 5, 2]]
    fieldName2 = "new_field2"
    load_array(timeseries, array=data2, field=fieldName2, verbose=True, dataFormat="row", interpolate=True)
    assert fieldName2 in timeseries.columns
    assert timeseries[fieldName2].to_list() == [9., 7., 5., 2.]
    assert timeseries[timeseries.timeName].to_list() == [1., 3., 5., 10.]

def test_load_uniform(timeseries):
    fieldName = "new_field"
    value = 2
    
    #Cannot load uniform data with a time series that has no time
    with pytest.raises(ValueError):
        load_uniform(timeseries, field=fieldName, value=value, verbose=True)
    
    timeseries[timeseries.timeName] = [1, 3, 5]
    load_uniform(timeseries, field=fieldName, value=value, verbose=True)
    
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [value]*3
    assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]

def test_load_function(timeseries):
    fieldName = "new_field"
    func = lambda x: x**2
    timeseries.loadArray([[1,1], [2,2], [3,3]], "var", verbose=True)
    load_function(timeseries, field=fieldName, function=func, verbose=True)
    
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [1, 4, 9]
    assert timeseries[timeseries.timeName].to_list() == [1, 2, 3]

def test_load_calculated(timeseries):
    fieldName = "new_field"
    func = lambda x: x**2
    timeseries.loadArray([[1,2], [2,3], [3,4]], "x", verbose=True)
    load_calculated(timeseries, field=fieldName, function=func, verbose=True)
    
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [4, 9, 16]
    assert timeseries[timeseries.timeName].to_list() == [1, 2, 3]
    
    func2 = lambda y: y + 1
    with pytest.raises(ValueError):
        load_calculated(timeseries, field=fieldName, function=func2, verbose=True)
        
    with pytest.raises(TypeError):
        load_calculated(timeseries, field=fieldName, function=2, verbose=True)
    
def test_loadField():
    # Test loading a field using the `loadField` method with different loading methods
    
    # Test LoadingMethod.FILE
    timeseries =  TimeSeries()
    fieldName = "new_field"
    with tempfile.NamedTemporaryFile(delete=True, mode="w") as temp_file:
        temp_file.write("1 2\n3 4\n5 6\n")
        temp_file.flush()
        temp_file_path = temp_file.name
        loadField(timeseries, field=fieldName, method="file", filename=temp_file_path, verbose=True)
        assert fieldName in timeseries.columns
        assert timeseries[fieldName].to_list() == [2, 4, 6]
        assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
    
    # Test LoadingMethod.ARRAY
    timeseries =  TimeSeries()
    fieldName = "new_field"
    data = [[1, 2], [3, 4], [5, 6]]
    loadField(timeseries, field=fieldName, method="array", array=data, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [2, 4, 6]
    assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
    
    # Test LoadingMethod.UNIFORM
    timeseries =  TimeSeries()
    fieldName = "new_field"
    timeseries[timeseries.timeName] = [1, 3, 5]
    value = 2
    loadField(timeseries, field=fieldName, method="uniform", value=value, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [value] * 3
    assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
    
    #Alias: constant
    timeseries =  TimeSeries()
    fieldName = "new_field"
    timeseries[timeseries.timeName] = [1, 3, 5]
    value = 2
    loadField(timeseries, field=fieldName, method="constant", value=value, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [value] * 3
    assert timeseries[timeseries.timeName].to_list() == [1, 3, 5]
    
    
    # Test LoadingMethod.FUNCTION
    timeseries =  TimeSeries()
    fieldName = "new_field"
    func = lambda x: x**2
    timeseries.loadArray([[1, 1], [2, 2], [3, 3]], "var", verbose=True)
    loadField(timeseries, field=fieldName, method="function", function=func, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [1, 4, 9]
    assert timeseries[timeseries.timeName].to_list() == [1, 2, 3]
    
    # Test LoadingMethod.CALCULATED
    timeseries =  TimeSeries()
    fieldName = "new_field"
    func = lambda x: x**2
    timeseries.loadArray([[1, 2], [2, 3], [3, 4]], "x", verbose=True)
    loadField(timeseries, field=fieldName, method="calculated", function=func, verbose=True)
    assert fieldName in timeseries.columns
    assert timeseries[fieldName].to_list() == [4, 9, 16]
    assert timeseries[timeseries.timeName].to_list() == [1, 2, 3]