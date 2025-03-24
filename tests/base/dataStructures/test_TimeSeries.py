import pytest
from pandas import DataFrame as df
import numpy as np
import tempfile
import os
from pathlib import Path
from libICEpost.src.base.dataStructures._TimeSeries import TimeSeries, TimeSeriesWarning

def test_initialization():
    ts = TimeSeries(timeName="time")
    assert ts.timeName == "time"
    assert ts._data.empty

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.TimeSeriesWarning")
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_loadArray():
    ts = TimeSeries(timeName="time")
    data = [(1, 2), (2, 3), (3, 4)]
    ts.loadArray(data, "var1", dataFormat="column")
    assert "var1" in ts.columns
    assert len(ts) == 3
    
    # Test row format
    ts = TimeSeries()
    data = [(1, 2, 3), (2, 3, 4)]
    ts.loadArray(data, "var1", dataFormat="row")
    assert len(ts) == 3
    
    # Test invalid data
    data = [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    with pytest.raises(ValueError):
        ts.loadArray(data, "var2")
        
    data = [([1], [2], [3]), ([2], [3], [4]), ([3], [4], [5])]
    with pytest.raises(ValueError):
        ts.loadArray(data, "var2")
        
    data = [(1, 2, 3), ("a", "b", "c")]
    with pytest.raises(TypeError):
        ts.loadArray(data, "var2", dataFormat="row")
        
    data = [(1, "2", 3), ("a", "b", "c")]
    with pytest.raises(TypeError):
        ts.loadArray(data, "var2", dataFormat="row")
    
    data = [(1, 2), (2, 3), (3, 4)]
    with pytest.raises(ValueError):
        ts.loadArray(data, "var1", dataFormat="row")
        
    data = [(1, 2, 3), (2, 3, 4)]
    with pytest.raises(ValueError):
        ts.loadArray(data, "var1", dataFormat="column")
        
    with pytest.raises(ValueError):
        ts.loadArray(data, "var1", dataFormat="a")
    
    # Additional tests for loadArray
    ts = TimeSeries()

    # Loading from list containing two lists for CA and variable (by row)
    ts = TimeSeries(timeName="CA")
    data = [[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]]
    ts.loadArray(data, "var1", dataFormat="row")
    #    CA  var1
    # 0   1    11
    # 1   2    12
    # 2   3    13
    # 3   4    14
    # 4   5    15

    # Loading second variable from list of (CA,var) pairs (order by column) without interpolation
    data = [(3, 3), (4, 3.5), (5, 2.4), (6, 5.2), (7, 3.14)]
    ts.loadArray(data, "var2", dataFormat="column")
    #    CA  var1  var2
    # 0   1  11.0   NaN
    # 1   2  12.0   NaN
    # 2   3  13.0  3.00
    # 3   4  14.0  3.50
    # 4   5  15.0  2.40
    # 5   6   NaN  5.20
    # 6   7   NaN  3.14
    assert "var2" in ts.columns
    assert len(ts) == 7
    assert np.isnan(ts["var2"][[0,1]]).all()
    assert np.isnan(ts["var1"][[5,6]]).all()

    # Extend the interval of var2 from a pandas.DataFrame with data by column,
    # suppressing the warning for orverwriting.
    data = df({"CA":[8, 9, 10, 11], "var":[2, 1, 0, -1]})
    ts.loadArray(data, "var2", dataFormat="column", verbose=False)
    #     CA  var1  var2
    # 0    1  11.0   NaN
    # 1    2  12.0   NaN
    # 2    3  13.0  3.00
    # 3    4  14.0  3.50
    # 4    5  15.0  2.40
    # 5    6   NaN  5.20
    # 6    7   NaN  3.14
    # 7    8   NaN  2.00
    # 8    9   NaN  1.00
    # 9   10   NaN  0.00
    # 10  11   NaN -1.00
    assert len(ts) == 11
    assert np.isnan(ts["var1"][[7,8,9,10]]).all()
    
    with pytest.warns(TimeSeriesWarning):
        ts.loadArray(data, "var2", dataFormat="column", verbose=True)

    # Load a variable var3 from numpy ndarray and interpolate
    data = np.array([[-5.5, 5.5],[2.3, 5.4]])
    ts.loadArray(data, "var3", dataFormat="row", interpolate=True)
    #       CA  var1  var2      var3
    # 0   -5.5   NaN   NaN  2.300000
    # 1    1.0  11.0   NaN  4.131818
    # 2    2.0  12.0   NaN  4.413636
    # 3    3.0  13.0  3.00  4.695455
    # 4    4.0  14.0  3.50  4.977273
    # 5    5.0  15.0  2.40  5.259091
    # 6    5.5   NaN  3.80  5.400000
    # 7    6.0   NaN  5.20       NaN
    # 8    7.0   NaN  3.14       NaN
    # 9    8.0   NaN  2.00       NaN
    # 10   9.0   NaN  1.00       NaN
    # 11  10.0   NaN  0.00       NaN
    # 12  11.0   NaN -1.00       NaN
    assert "var3" in ts.columns
    assert len(ts) == 13
    assert np.isnan(ts["var3"][[7,8,9,10,11,12]]).all()
    assert np.isnan(ts["var1"][0])
    assert np.isnan(ts["var2"][0])

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.TimeSeriesWarning")
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_loadFile(tmp_path):
    with tempfile.TemporaryDirectory() as folder:
        ts = TimeSeries(timeName="time")
        data = "1 2\n2 3\n3 4"
        file_path = str(Path(folder) / "test_file.txt")
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", delimiter=" ")
        assert "var1" in ts.columns
        assert len(ts) == 3
        
        # different column
        ts = TimeSeries(timeName="time")
        data = "1 2 3\n2 3 4\n3 4 5"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", x_col=1, y_col=2)
        assert len(ts) == 3
        
        #Header and trailing lines
        ts = TimeSeries(timeName="time")
        data = "Header\n1 2 3\n2 3 4\n3 4 5\nTrailing"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", x_col=1, y_col=2, skip_rows=1, max_rows=3)
        assert len(ts) == 3
        
        #offset and scale
        ts = TimeSeries(timeName="time")
        data = "1 2\n2 3\n3 4"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", x_off=1, x_scale=0.5, y_off=2, y_scale=2)
        assert np.array_equal(ts["time"].to_numpy(), [1, 1.5, 2])
        assert np.array_equal(ts["var1"].to_numpy(), [8, 10, 12])
        
        #Different delimiter
        ts = TimeSeries(timeName="time")
        data = "1,2\n2,3\n3,4"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", delimiter=",")
        assert len(ts) == 3
        
        #Comments
        ts = TimeSeries(timeName="time")
        data = "#1 2\n2 3\n3 4"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", delimiter=" ", comment="#")
        assert len(ts) == 2
        
        #Aliases
        ts = TimeSeries(timeName="time")
        data = "1 2\n2 3\n3 4"
        with open(file_path, "w") as file:
            file.write(data)
        ts.loadFile(file_path, "var1", delimiter=" ", xOff=1, xScale=0.5, yOff=2, yScale=2)
        assert np.array_equal(ts["time"].to_numpy(), [1, 1.5, 2])
        assert np.array_equal(ts["var1"].to_numpy(), [8, 10, 12])
        
        #Multiple equivalent kwargs
        ts = TimeSeries(timeName="time")
        data = "1 2\n2 3\n3 4"
        with open(file_path, "w") as file:
            file.write(data)
        with pytest.raises(ValueError):
            ts.loadFile(file_path, "var1", delimiter=" ", x_off=1, xOff=2)
            
        #Deprecated kwargs
        kwargs = {"CAOff": 1, "CACol": 0, "CAscale":0.5, "varCol":1, "varOff": 2, "varScale": 2}
        for key, value in kwargs.items():
            with pytest.warns(DeprecationWarning):
                ts.loadFile(file_path
                            , "var1"
                            , delimiter=" "
                            , **{key: value})
    
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.TimeSeriesWarning")
@pytest.mark.filterwarnings("error::DeprecationWarning")    
def test_interpolator():
    ts = TimeSeries(timeName="time")
    data = [(1, 2), (2, 3), (3, 4)]
    ts.loadArray(data, "var1", dataFormat="column")
    assert ts.var1(2.5) == 3.5
    
    #Loading reserved or invalid variables
    with pytest.raises(ValueError):
        ts.loadArray(data, "loc", dataFormat="column")
        ts.__getattribute__("loc")
    with pytest.raises(ValueError):
        ts.loadArray(data, "a-a.c", dataFormat="column")
        ts.__getattribute__("a-a.c")

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.TimeSeriesWarning")
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_write(tmp_path):
    ts = TimeSeries(timeName="time")
    data = [(1, 2), (2, 3), (3, 4)]
    ts.loadArray(data, "var1", dataFormat="column")
    
    with tempfile.TemporaryDirectory() as folder:
        file_path = str(Path(folder) / "test_file.txt")
        ts.write(file_path, overwrite=True)
        assert os.path.exists(file_path)
        
        with pytest.raises(FileExistsError):
            ts.write(file_path, overwrite=False)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.TimeSeriesWarning")
@pytest.mark.filterwarnings("error::DeprecationWarning")
def test_plot():
    ts = TimeSeries(timeName="time")
    data = [(1, 2), (2, 3), (3, 4)]
    ts.loadArray(data, "var1", dataFormat="column")
    plot = ts.plot()
    assert plot is not None
    
def test_loc_iloc():
    ts = TimeSeries(timeName="time")
    data = [(1, 2), (2, 3), (3, 4)]
    ts.loadArray(data, "var1", dataFormat="column")
    
    ts.iloc[0] = [0, 1]
    assert np.array_equal(ts.iloc[0], [0, 1])
    
    ts.loc[:, "var1"] = [4, 5, 6]
    assert np.array_equal(ts["var1"], [4, 5, 6])
    
    #Assert interpolation after setting values
    assert ts.var1(1.) == 4.5