from libICEpost.src.base.Functions.userInterface import loadDictionary
import os, tempfile
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

def test_loadDictionary():
    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a temporary dictionary file
        dict_path = os.path.join(tmpdirname, "testDict")
        with open(dict_path, 'w') as f:
            f.write(
"""
var1 = 1
var2 = "Hello"
var3 = [1, 2, 3]

dict1 = {"key1": "value1", "key2": "value2"}
""")
        
        # Create a temporary template file
        template_path = os.path.join(tmpdirname, "template")
        with open(template_path, 'w') as f:
            f.write(
"""
var1 = 2
var2 = "World"
var3 = [4, 5, 6]

dict1 = {"key3": "value3", "key4": "value4"}
""")
        
        # Test loading the dictionary without templates
        D = loadDictionary(dict_path)
        assert isinstance(D, Dictionary)
        
        # Test loading the dictionary with templates
        D = loadDictionary(dict_path, template_path)
        assert isinstance(D, Dictionary)
        
        # Check if the values are updated correctly
        assert D["var1"] == 1
        assert D["var2"] == "Hello"
        assert D["var3"] == [1, 2, 3]
        assert D["dict1"]["key3"] == "value3"
        assert D["dict1"]["key4"] == "value4"
        assert D["dict1"]["key1"] == "value1"
        assert D["dict1"]["key2"] == "value2"