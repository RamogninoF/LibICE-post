import pytest
import tempfile
import os
import struct

from libICEpost.src.base.Functions.functionsForOF import readOFscalarList, writeOFscalarList

def test_readOFscalarList():
    # Create a temporary file with a scalarList
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(b"FoamFile\n{\n    version     2.0;\n    format      ascii;\n    class       scalarList;\n    location    \"0\";\n    object      test;\n}\n\n10\n(\n1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0\n)\n")
        tmpfile_name = tmpfile.name

    # Test reading the scalarList
    result = readOFscalarList(tmpfile_name)
    assert result == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    # Clean up
    os.remove(tmpfile_name)

def test_readOFscalarList_ioerror():
    with pytest.raises(IOError):
        readOFscalarList("non_existent_file")

def test_readOFscalarList_binary():
    # Create a temporary file with a binary scalarList
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    binary_data = struct.pack('10d', *values)
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(b"FoamFile\n{\n    version     2.0;\n    format      binary;\n    class       scalarList;\n    location    \"0\";\n    object      test;\n}\n\n10\n(" + binary_data + b")\n\n")
        tmpfile_name = tmpfile.name

    # Test reading the binary scalarList
    result = readOFscalarList(tmpfile_name)
    assert result == values

    # Clean up
    os.remove(tmpfile_name)

def test_writeOFscalarList():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile_name = tmpfile.name

    # Test writing the scalarList
    writeOFscalarList(values, tmpfile_name, overwrite=True, binary=False)

    # Verify the content of the file
    with open(tmpfile_name, 'r') as f:
        content = f.read()
        assert "scalarList" in content
        assert "1.0 2.0 3.0 4.0 5.0" in content

    # Clean up
    os.remove(tmpfile_name)

def test_writeOFscalarList_binary():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile_name = tmpfile.name

    # Test writing the scalarList in binary mode
    writeOFscalarList(values, tmpfile_name, overwrite=True, binary=True)

    # Verify the content of the file
    with open(tmpfile_name, 'rb') as f:
        content = f.read()
        assert b"scalarList" in content
        binary_data = struct.pack('5d', *values)
        assert binary_data in content

    # Clean up
    os.remove(tmpfile_name)

def test_writeOFscalarList_ioerror():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile_name = tmpfile.name
    
    # Test writing the scalarList in read-only mode
    with pytest.raises(IOError):
        writeOFscalarList(values, tmpfile_name, overwrite=False, binary=False)
            
    os.chmod(tmpfile_name, 0o400)  # Make the file read-only

    try:
        with pytest.raises(IOError):
            writeOFscalarList(values, tmpfile_name, overwrite=True, binary=False)
    finally:
        os.chmod(tmpfile_name, 0o600)  # Restore write permission to clean up
        os.remove(tmpfile_name)

def test_write_and_readOFscalarList_binary():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile_name = tmpfile.name

    # Test writing the scalarList in binary mode
    writeOFscalarList(values, tmpfile_name, overwrite=True, binary=True)

    # Test reading the binary scalarList
    result = readOFscalarList(tmpfile_name)
    assert result == values

    # Clean up
    os.remove(tmpfile_name)