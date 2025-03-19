import pytest
import numpy as np
import pandas as pd
import os
import shutil
from libICEpost.src.base.dataStructures.Tabulation.OFTabulation import OFTabulation
import tempfile

def test_OFTabulation_construction():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    assert table.shape == (3, 2)
    assert table.size == 6
    assert table.order == ["x", "y"]
    assert table.fields == ["z"]
    assert table.files == {"z": "z"}
    assert table.inputVariables == ["x", "y"]
    assert table.names == {"x":"x", "y":"y"}
    assert np.array_equal(table.ranges["x"], np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(table.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))
    assert table.tables["z"].shape == (3, 2)
    assert table.tables["z"].size == 6
    assert table.tables["z"].order == ["x", "y"]
    assert np.array_equal(table.tables["z"].ranges["x"], table.ranges["x"])
    assert np.array_equal(table.tables["z"].ranges["y"], table.ranges["y"])
    assert table.path is None
    assert table.tableProperties == {"xValues":[0.0, 1.0, 2.0], "yValues":[0.0, 1.0], "fields":["z"], "inputVariables":["x", "y"]}

    table2 = OFTabulation(
        ranges=ranges,
        data=data,
        order=order,
        files={"z": "file"}, #Use file instead of z
        inputNames={"x":"X"}, #Rename x to X
        outputNames={"z":"Z"}, #Rename z to Z
        path="path",
        tablePropertiesParameters={"other": "other"} #Add other parameter to table properties
        )
    assert table2.inputVariables == ["x", "y"]
    assert table2.names == {"x":"X", "y":"y"}
    assert table2.fields == ["Z"]
    assert table2.files == {"Z": "file"}
    assert table2.path == "path"
    assert "other" in table2.tableProperties
    assert table2.tableProperties["other"] == "other"

    #Assert wrong input
    with pytest.raises(ValueError):
        OFTabulation(ranges=ranges, data=data, order=["x", "y", "z"])
    with pytest.raises(ValueError):
        OFTabulation(ranges=ranges, data=data, order=["x"])
    with pytest.raises(ValueError):
        OFTabulation(ranges=ranges, data=data, order=order, files={"x": "file"})
    with pytest.raises(ValueError):
        OFTabulation(ranges=ranges, data=data, order=order, inputNames={"x":"X", "z":"Z"})
    with pytest.raises(ValueError):
        OFTabulation(ranges=ranges, data=data, order=order, outputNames={"x":"X", "z":"Z"})


def test_OFTabulation_concat():
    ranges1 = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data1 = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order1 = ["x", "y"]
    
    table1 = OFTabulation(ranges=ranges1, data=data1, order=order1)
    
    ranges2 = {
        "x": [3.0, 4.0],
        "y": [0.0, 1.0]
    }
    data2 = {
        "z": [6.0, 7.0, 8.0, 9.0]
    }
    order2 = ["x", "y"]
    
    table2 = OFTabulation(ranges=ranges2, data=data2, order=order2)
    
    table3 = table1 + table2
    
    assert table3.shape == (5, 2)
    assert table3.size == 10
    assert table3.order == ["x", "y"]
    assert table3.fields == ["z"]
    assert np.array_equal(table3.ranges["x"], np.array([0.0, 1.0, 2.0, 3.0, 4.0]))
    assert np.array_equal(table3.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table3.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]))
    
    table1 += table2
    
    assert table1.shape == (5, 2)
    assert table1.size == 10
    assert table1.order == ["x", "y"]
    assert table1.fields == ["z"]
    assert np.array_equal(table1.ranges["x"], np.array([0.0, 1.0, 2.0, 3.0, 4.0]))
    assert np.array_equal(table1.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table1.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]))

    # Assert wrong input
    ranges3 = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0, 2.0]
    }
    data3 = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    }
    order3 = ["x", "y"]
    
    table3 = OFTabulation(ranges=ranges3, data=data3, order=order3)
    
    with pytest.raises(ValueError):
        table1 + table3
    with pytest.raises(ValueError):
        table1 += table3

def test_OFTabulation_reorder():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    assert table.order == ["x", "y"]
    assert table.tables["z"].order == ["x", "y"]
    
    table.order = ["y", "x"]
    
    assert table.order == ["y", "x"]
    assert table.tables["z"].order == ["y", "x"]
    
    with pytest.raises(ValueError):
        table.order = ["x", "z"]
    
    with pytest.raises(ValueError):
        table.order = ["x"]
    
    with pytest.raises(ValueError):
        table.order = ["x", "y", "z"]

def test_OFTabulation_write_read():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    with tempfile.TemporaryDirectory() as masterPath:
        path = masterPath + "/table"
        table = OFTabulation(ranges=ranges, data=data, order=order, path=path)
        #Try to write the table in no-write mode
        with pytest.raises(IOError):
            table.write()

        table.noWrite = False
        table.write()
        
        #Check the structure of the written table
        assert os.path.exists(path)
        assert os.path.exists(path + "/constant")
        assert os.path.exists(path + "/system")
        assert os.path.exists(path + "/system/controlDict")
        assert os.path.exists(path + "/tableProperties")
        for f in table.fields:
            assert os.path.exists(path + "/constant/" + table.files[f])
        
        #Read table properties
        from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
        tableProperties = ParsedParameterFile(path + "/tableProperties", noHeader=True)
        assert tableProperties["fields"] == ["z"]
        assert tableProperties["inputVariables"] == ["x", "y"]
        assert np.array_equal(tableProperties["xValues"], np.array([0.0, 1.0, 2.0]))
        assert np.array_equal(tableProperties["yValues"], np.array([0.0, 1.0]))
        assert tableProperties["inputVariables"] == ["x", "y"]
        
        #Write to different path
        table.write(path=path + "2")
        
        #Try to write in binary mode
        table.write(path=path + "3", binary=True)
        
        #Try overwriting
        with pytest.raises(IOError):
            table.write()
        table.write(overwrite=True)
        
        # Read the table back
        table_read = OFTabulation.fromFile(path=path)
        
        assert table == table_read
        
        # Read the table with different variable name
        table_read2 = OFTabulation.fromFile(path=path, files={"Z": "z"}, outputNames={"z":"Z"})

        with pytest.raises(IOError):
            OFTabulation.fromFile(path=path, files={"z": "aaa"})
        with pytest.raises(IOError):
            OFTabulation.fromFile(path=path, outputNames={"z": "Z"}, files={"z": "aaa"})

        assert table_read2.fields == ["Z"]
        assert table_read2.files == {"Z": "z"}
        assert table_read2.tables["Z"] == table.tables["z"]
        
        #Read table with different input names
        table_read3 = OFTabulation.fromFile(path=path, inputNames={"x":"X"})
        assert table_read3.inputVariables == ["X", "y"]
        assert table_read3.order == ["X", "y"]
        assert table_read3.names == {"X":"x", "y":"y"}
        assert table_read3.tables["z"].order == ["X", "y"]
        assert np.array_equal(table_read3.tables["z"].ranges["X"], table.tables["z"].ranges["x"])

def test_OFTabulation_slice():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Slice by index
    slices = [slice(0, 2), slice(0, 2)]
    sliced_table = table.slice(slices=slices)
    assert sliced_table.shape == (2, 2)
    assert sliced_table.size == 4
    assert np.array_equal(sliced_table.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0]))
    for r in sliced_table.ranges:
        assert np.array_equal(sliced_table.ranges[r], ranges[r][slices[order.index(r)]])
        for t in sliced_table.fields:
            assert np.array_equal(sliced_table.tables[t].ranges[r], sliced_table.ranges[r])
    
    # Slice by ranges
    sliceRanges = {"x": [0.0, 2.0], "y": [0.0]}
    sliced_table = table.slice(ranges=sliceRanges)
    assert sliced_table.shape == (2, 1)
    assert sliced_table.size == 2
    assert np.array_equal(sliced_table.tables["z"].data.flatten(), np.array([0.0, 4.0]))
    for r in sliced_table.ranges:
        assert np.array_equal(sliced_table.ranges[r], sliceRanges[r])
        for t in sliced_table.fields:
            assert np.array_equal(sliced_table.tables[t].ranges[r], sliced_table.ranges[r])
    
    # Assert wrong input
    with pytest.raises(ValueError):
        table.slice()
    with pytest.raises(ValueError):
        table.slice(slices=[slice(0, 2)], ranges={"x": [0.0, 2.0]})
    with pytest.raises(IndexError):
        table.slice(slices=[[0, 4], slice(0, 2)])
    with pytest.raises(IndexError):
        table.slice(slices=[4, slice(0, 2)])
    with pytest.raises(ValueError):
        table.slice(ranges={"x": [0.0, 3.0], "y": [0.0]})
    with pytest.raises(TypeError):
        table.slice(slices="a")

def test_OFTabulation_insertDimension():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Insert dimension
    new_table = table.insertDimension(variable="w", value=0.5, index=0)
    assert new_table.shape == (1, 3, 2)
    assert new_table.size == 6
    assert new_table.order == ["w", "x", "y"]
    assert new_table.fields == ["z"]
    assert np.array_equal(new_table.ranges["w"], np.array([0.5]))
    assert np.array_equal(new_table.ranges["x"], np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(new_table.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(new_table.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))
    
    # Insert dimension in-place
    table.insertDimension(variable="w", value=0.5, index=0, inplace=True)
    assert table.shape == (1, 3, 2)
    assert table.size == 6
    assert table.order == ["w", "x", "y"]
    assert table.fields == ["z"]
    assert np.array_equal(table.ranges["w"], np.array([0.5]))
    assert np.array_equal(table.ranges["x"], np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(table.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))
    
    # Assert wrong input
    with pytest.raises(IndexError):
        table.insertDimension(variable="w", value=0.5, index=4)
    with pytest.raises(TypeError):
        table.insertDimension(variable="w", value="a", index=0)
    with pytest.raises(TypeError):
        table.insertDimension(variable=0.5, value=0.5, index=0)

def test_OFTabulation_toPandas():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Convert to pandas DataFrame
    df = table.toPandas()
    
    assert df.shape == (6, 3)
    assert list(df.columns) == ["x", "y", "z"]
    assert np.array_equal(df["x"].values, np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0]))
    assert np.array_equal(df["y"].values, np.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0]))
    assert np.array_equal(df["z"].values, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))

def test_OFTabulation_fromPandas():
    data = {
        "x": [0.0, 0.0, 1.0, 1.0, 2.0, 2.0],
        "y": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    df = pd.DataFrame(data)
    order = ["x", "y"]
    
    table = OFTabulation.fromPandas(df, order)
    
    assert table.shape == (3, 2)
    assert table.size == 6
    assert table.order == order
    assert table.fields == ["z"]
    assert np.array_equal(table.ranges["x"], np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(table.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table.tables["z"].data.flatten(), np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))

    #Try with different order
    order2 = ["y", "x"]
    table = OFTabulation.fromPandas(df, order2)
    
    assert table.shape == (2, 3)
    assert table.size == 6
    assert table.order == order2
    assert table.fields == ["z"]
    assert np.array_equal(table.ranges["x"], np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(table.ranges["y"], np.array([0.0, 1.0]))
    assert np.array_equal(table.tables["z"].data.flatten(), np.array([0.0, 2.0, 4.0, 1.0, 3.0, 5.0]))

    # Assert wrong input
    with pytest.raises(ValueError):
        OFTabulation.fromPandas(df, ["x", "y", "z"])
    with pytest.raises(ValueError):
        OFTabulation.fromPandas(df, ["x"])
    with pytest.raises(ValueError):
        OFTabulation.fromPandas(df, ["a", "b"])

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_OFTabulation_call():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Interpolate values
    assert table("z", 0.0, 0.0) == 0.0
    assert table("z", 1.0, 1.0) == 3.0
    assert table("z", 2.0, 0.0) == 4.0
    assert np.array_equal(table("z", [0, 1], [2, 1]), [1, 5])
    assert np.isnan(table("z", 0.0, 5.0, outOfBounds="nan"))
    
    # Assert wrong input
    with pytest.raises(ValueError):
        table("a", 0.0, 0.0)
    with pytest.raises(ValueError):
        table("z", 3.0, 0.0)
    with pytest.raises(ValueError):
        table("z", 0.0, 2.0)
    with pytest.raises(ValueError):
        table("z", [0, 0], [5, 0])

def test_OFTabulation_access_methods():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Test setFile
    table.setFile("z", "new_file")
    assert table.files["z"] == "new_file"
    
    # Test setTable
    new_data = [5.0, 4.0, 3.0, 2.0, 1.0, 0.0]
    new_table = OFTabulation(ranges=ranges, data={"z": new_data}, order=order)
    table.setTable("z", new_table.tables["z"])
    assert np.array_equal(table.tables["z"].data.flatten(), np.array(new_data))
    
    # Test addField
    table.addField(data=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0], field="w")
    assert "w" in table.fields
    assert np.array_equal(table.tables["w"].data.flatten(), np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0]))
    
    # Test delField
    table.delField("w")
    assert "w" not in table.fields
    
    # Test setName
    table.setName("x", "X")
    assert table.names["x"] == "X"
    
    # Test outOfBounds
    table.outOfBounds("z", "nan")
    assert table.outOfBounds("z") == "nan"
    
    # Assert wrong input
    with pytest.raises(ValueError):
        table.setFile("a", "file")
    with pytest.raises(ValueError):
        table.setTable("a", new_table.tables["z"])
    with pytest.raises(ValueError):
        table.addField(data=[10.0, 20.0], field="w")
    with pytest.raises(ValueError):
        table.addField(data=table.tables["z"].data, field="z")
    with pytest.raises(ValueError):
        table.delField("a")
    with pytest.raises(ValueError):
        table.setName("a", "A")
    with pytest.raises(KeyError):
        table.outOfBounds("a", "nan")
    with pytest.raises(ValueError):
        table.outOfBounds("z", "clamp")

def test_OFTabulation_str_repr():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Test __str__
    str_table = str(table)
    # Test __repr__
    repr_table = repr(table)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_plot():
    """
    Test the plot method of the Tabulation class.
    """
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Test plot method
    ax = table.plot(field="z", x="x", c="y", iso={"y": 1.0})
    
    from matplotlib import pyplot as plt
    ax = plt.subplot()
    ax = table.plot(field="z", x="x", c="y", iso={"y": 1.0}, ax=ax, xlabel="X", ylabel="Y", title="Title", colorMap="viridis")
    
    with pytest.raises(ValueError):
        table.plot(field="z", x="x", c="y", iso={"z": 1.0})
    
    with pytest.raises(ValueError):
        table.plot(field="z", x="y", c="y", iso={"x": 0.5})
        
def test_OFTabulation_setRange():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    table = OFTabulation(ranges=ranges, data=data, order=order)
    
    # Test setRange
    table.setRange("x", [0.0, 2.0, 4.0])
    assert np.array_equal(table.ranges["x"], np.array([0.0, 2.0, 4.0]))
    
    with pytest.raises(ValueError):
        table.setRange("x", [0, 1, 2, 3])
    with pytest.raises(ValueError):
        table.setRange("x", [0, 0, 3])
    with pytest.raises(ValueError):
        table.setRange("x", [2, 0, 3])
    with pytest.raises(ValueError):
        table.setRange("k", [0, 1, 2, 3])

def test_OFTabulation_clip():
    ranges = {
        "x": [0.0, 1.0, 2.0],
        "y": [0.0, 1.0]
    }
    data = {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    }
    order = ["x", "y"]
    
    tab = OFTabulation(ranges=ranges, data=data, order=order)
    
    #Key word arguments
    tab_clip = tab.clip(x=(1,2))
    assert tab_clip.shape == (2, 2)
    assert np.array_equal(tab_clip.ranges["x"], np.array([1,2]))
    assert np.array_equal(tab_clip.ranges["x"], tab_clip.tables["z"].ranges["x"])
    
    #Both
    tab_clip = tab.clip(x=(0,1), ranges={"y": (1,2)})
    assert tab_clip.shape == (2, 1)
    assert np.array_equal(tab_clip.ranges["x"], np.array([0,1]))
    assert np.array_equal(tab_clip.ranges["y"], np.array([1]))
    assert np.array_equal(tab_clip.ranges["x"], tab_clip.tables["z"].ranges["x"])
    assert np.array_equal(tab_clip.ranges["y"], tab_clip.tables["z"].ranges["y"])
    
    #None
    tab_clip = tab.clip(x=(None, 1))
    assert tab_clip.shape == (2, 2)
    assert np.array_equal(tab_clip.ranges["x"], np.array([0,1]))
    assert np.array_equal(tab_clip.ranges["x"], tab_clip.tables["z"].ranges["x"])
    
    tab_clip = tab.clip(x=(None,None))
    assert tab_clip == tab
    
    #Errors
    with pytest.raises(TypeError):
        tab.clip(x=(0,1), ranges={"y": [0,2]})
    with pytest.raises(ValueError):
        tab.clip(x=(0,1), ranges={"k": (0,2)})
    with pytest.raises(ValueError):
        tab.clip(x=(0,1), ranges={"y": (0,2,3)})
    with pytest.raises(ValueError):
        tab.clip(x=(0,1), ranges={"y": (2,1)})
    with pytest.raises(ValueError):
        tab.clip(x=(0,1), ranges={"y": (0,2)}, y=(0,1))
    
    #Inplace
    tab.clip(x=(-5,1), inplace=True)
    assert tab.shape == (2, 2)
    assert np.array_equal(tab.ranges["x"], np.array([0,1]))
    