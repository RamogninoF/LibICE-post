import pytest
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

def defineClasses():
    class TestBaseClass(BaseClass):
        pass

        @abstractmethod
        def method(self):
            pass

    class TestChildClassVirtual(TestBaseClass):
        pass

    class TestChildClassConcrete(TestBaseClass):
        @classmethod
        def fromDictionary(cls, dictionary: dict) -> BaseClass:
            instance = cls()
            for key, value in dictionary.items():
                setattr(instance, key+"_concrete", value)
            return instance

        def method(self):
            pass
        
    return TestBaseClass, TestChildClassVirtual, TestChildClassConcrete
    
def test_create_runtime_selection_table():
    TestBaseClass, TestChildClassVirtual, TestChildClassConcrete = defineClasses()
    assert not TestBaseClass.hasSelectionTable()
    
    TestBaseClass.createRuntimeSelectionTable()
    assert TestBaseClass.hasSelectionTable()
    with pytest.raises(ValueError):
        TestBaseClass.createRuntimeSelectionTable()

def test_add_to_runtime_selection_table():
    TestBaseClass, TestChildClassVirtual, TestChildClassConcrete = defineClasses()
    TestBaseClass.createRuntimeSelectionTable()
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassVirtual)
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassConcrete)
    
    assert TestChildClassVirtual.__name__ in TestBaseClass.selectionTable()
    assert TestChildClassConcrete.__name__ in TestBaseClass.selectionTable()
    
    with pytest.raises(ValueError):
        TestBaseClass.addToRuntimeSelectionTable(TestChildClassVirtual, overwrite=False)

def test_selector():
    TestBaseClass, TestChildClassVirtual, TestChildClassConcrete = defineClasses()
    
    with pytest.raises(ValueError):
        TestBaseClass.selectionTable()
    
    with pytest.raises(ValueError):
        TestBaseClass.addToRuntimeSelectionTable(TestChildClassVirtual)
    
    with pytest.raises(ValueError):
        TestBaseClass.selector("TestChildClassConcrete", {})
    
    TestBaseClass.createRuntimeSelectionTable()
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassConcrete)
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassVirtual)
    instance = TestBaseClass.selector("TestChildClassConcrete", {"attr": "value"})
    assert isinstance(instance, TestChildClassConcrete)
    assert instance.attr_concrete == "value"
    
    with pytest.raises(ValueError):
        TestBaseClass.selector("NotChildClass", {})
    
    with pytest.raises(TypeError):
        TestBaseClass.selector("TestChildClassVirtual", {"attr": "value"})

def test_selection_table_add_non_subclass():
    TestBaseClass, TestChildClassVirtual, TestChildClassConcrete = defineClasses()
    TestBaseClass.createRuntimeSelectionTable()
    class NonSubclass:
        pass
    with pytest.raises(TypeError):
        TestBaseClass.selectionTable().add(NonSubclass)

def test_selection_table_getitem():
    TestBaseClass, TestChildClassVirtual, TestChildClassConcrete = defineClasses()
    TestBaseClass.createRuntimeSelectionTable()
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassConcrete)
    TestBaseClass.addToRuntimeSelectionTable(TestChildClassVirtual)
    assert TestBaseClass.selectionTable()["TestChildClassConcrete"] == TestChildClassConcrete
    assert TestBaseClass.selectionTable()["TestChildClassVirtual"] == TestChildClassVirtual
    with pytest.raises(ValueError):
        TestBaseClass.selectionTable()["NotChildClass"]