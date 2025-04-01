import pytest
from libICEpost.src.base.dataStructures.Dictionary import Dictionary, toDictionary

def test_dictionary_initialization():
    d = Dictionary(a=1, b=2)
    assert d['a'] == 1
    assert d['b'] == 2

def test_dictionary_fromFile(tmp_path):
    file_content = """
a = 1
b = 2
"""
    file_path = tmp_path / "test_file.py"
    file_path.write_text(file_content)

    d = Dictionary.fromFile(str(file_path))
    assert d['a'] == 1
    assert d['b'] == 2

def test_dictionary_lookup():
    d = Dictionary(a=1, b=2)
    assert d.lookup('a') == 1
    assert d.lookup('b') == 2
    with pytest.raises(KeyError):
        d.lookup('c')

def test_dictionary_lookup_with_type():
    d = Dictionary(a=1, b="string")
    assert d.lookup('a', varType=int) == 1
    assert d.lookup('b', varType=str) == "string"
    with pytest.raises(TypeError):
        d.lookup('a', varType=str)

def test_dictionary_pop():
    d = Dictionary(a=1, b=2)
    assert d.pop('a') == 1
    with pytest.raises(KeyError):
        d.pop('c')

def test_dictionary_lookupOrDefault():
    d = Dictionary(a=1, b=2)
    assert d.lookupOrDefault('a', default=0) == 1
    assert d.lookupOrDefault('c', default=0) == 0
    with pytest.raises(TypeError):
        d.lookupOrDefault('a', default="string")
    assert d.lookupOrDefault('a', default="string", fatal=False) == 1

def test_dictionary_update():
    d = Dictionary(a=1, b={'c': 2})
    d.update(a=3, b={'d': 4})
    assert d['a'] == 3
    assert d['b']['c'] == 2
    assert d['b']['d'] == 4

def test_dictionary_correctSubdicts():
    d = Dictionary(a=1, b={'c': 2})
    d._correctSubdicts()
    assert isinstance(d['b'], Dictionary)
    assert d['b']['c'] == 2

def test_dictionary_lookup_with_iterable_type():
    d = Dictionary(a=1, b="string", c=3.0)
    assert d.lookup('a', varType=(int, float)) == 1
    assert d.lookup('b', varType=(str,)) == "string"
    assert d.lookup('c', varType=(int, float)) == 3.0
    with pytest.raises(TypeError):
        d.lookup('b', varType=(int, float))
    
    with pytest.raises(TypeError):
        d.lookup('a', varType=(1,))

def test_toDictionary():
    # Test converting a regular dictionary to a Dictionary object
    regular_dict = {"a": 1, "b": {"c": 2}}
    converted_dict = toDictionary(regular_dict, name="TestDict")
    assert isinstance(converted_dict, Dictionary)
    assert converted_dict.name == "TestDict"
    assert isinstance(converted_dict["b"], Dictionary)
    assert converted_dict["b"].name == "TestDict.b"

    # Test passing an already converted Dictionary object
    existing_dict = Dictionary(a=1, b=2, _name="ExistingDict")
    result_dict = toDictionary(existing_dict)
    assert result_dict is existing_dict
    assert result_dict.name == "ExistingDict"

def test_dictionary_name_attribute():
    # Test the name attribute of the Dictionary class
    d = Dictionary(a=1, b=2, _name="MyDict")
    assert d.name == "MyDict"

    # Test sub-dictionaries inherit the correct name
    d["sub"] = {"c": 3}
    assert isinstance(d["sub"], Dictionary)
    assert d["sub"].name == "MyDict.sub"