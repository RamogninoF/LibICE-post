import pytest
import numpy as np
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
