import pytest
import tempfile
import os
import struct
import numpy as np

from libICEpost.src.base.Functions.functionsForOF import readOFscalarList, writeOFscalarList

def test_readOFscalarList():
    # Create a temporary file with a scalarList
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")
        with open(tmpfile_name, 'wb') as f:
            f.write(b"FoamFile\n{\n    version     2.0;\n    format      ascii;\n    class       scalarList;\n    location    \"0\";\n    object      test;\n}\n\n10\n(\n1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0\n)\n")

        # Test reading the scalarList
        result = readOFscalarList(tmpfile_name)
        assert np.allclose(result, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

def test_readOFscalarList_ioerror():
    with pytest.raises(IOError):
        readOFscalarList("non_existent_file")

def test_readOFscalarList_binary():
    # Create a temporary file with a binary scalarList
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    binary_data = struct.pack('10d', *values)
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")
        with open(tmpfile_name, 'wb') as f:
            f.write(b"FoamFile\n{\n    version     2.0;\n    format      binary;\n    class       scalarList;\n    location    \"0\";\n    object      test;\n}\n\n10\n(" + binary_data + b")\n\n")

        # Test reading the binary scalarList
        result = readOFscalarList(tmpfile_name)
        assert np.allclose(result, values)

def test_writeOFscalarList():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")

        # Test writing the scalarList
        writeOFscalarList(values, tmpfile_name, overwrite=True, binary=False)

        # Verify the content of the file
        with open(tmpfile_name, 'r') as f:
            content = f.read()
            assert "scalarList" in content
            assert "1.0 2.0 3.0 4.0 5.0" in content

def test_writeOFscalarList_binary():
    values = np.random.rand(5160)*1000
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")

        # Test writing the scalarList in binary mode
        writeOFscalarList(values, path=tmpfile_name, binary=True)

        # Verify the content of the file
        with open(tmpfile_name, 'rb') as f:
            content = f.read()
            assert b"scalarList" in content
            binary_data = struct.pack(f"{len(values)}d", *values)
            assert binary_data in content

def test_writeOFscalarList_ioerror():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")
        
        # Create the file first
        with open(tmpfile_name, 'w') as f:
            f.write("existing file")
        
        # Test writing the scalarList with overwrite=False
        with pytest.raises(IOError):
            writeOFscalarList(values, tmpfile_name, overwrite=False, binary=False)

def test_write_and_readOFscalarList_binary():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.TemporaryDirectory() as temp_dir:
        tmpfile_name = os.path.join(temp_dir, "test_scalarList")

        # Test writing the scalarList in binary mode
        writeOFscalarList(values, tmpfile_name, overwrite=True, binary=True)

        # Test reading the binary scalarList
        result = readOFscalarList(tmpfile_name)
        assert np.allclose(result, values)
