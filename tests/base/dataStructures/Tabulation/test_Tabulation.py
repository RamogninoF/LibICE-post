import pytest
import numpy as np
from pandas import DataFrame
from libICEpost.src.base.dataStructures.Tabulation.Tabulation import Tabulation, toPandas, TabulationAccessWarning, concat

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_constructor():
    """
    Test the Tabulation constructor with valid 3D data.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    assert tab.shape == (2, 3, 4)
    assert tab.ndim == 3
    assert tab.size == 24
    assert tab.order == order
    assert np.array_equal(tab.data, data)
    for i, key in enumerate(order):
        assert np.array_equal(tab.ranges[key], ranges[key])

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_getitem():
    """
    Test the __getitem__ method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test single index access
    assert tab[0] == 100
    assert tab[23] == 223
    
    # Test multi-index access
    assert tab[0, 0, 0] == 100
    assert tab[1, 2, 3] == 223
    
    assert np.array_equal(tab[0, :, :],data[0, :, :])
    assert np.array_equal(tab[[0,1], :, :],data[[0,1], :, :])
    
    # Test slicing
    assert np.array_equal(tab[0:12], data.flatten()[:12])
    assert np.array_equal(tab[12:], data.flatten()[12:])
    assert np.array_equal(tab[0:12:2], data.flatten()[:12:2])
    
    # Test negative slicing
    assert np.array_equal(tab[-1], data.flatten()[-1])
    
    # Test invalid index access
    with pytest.raises((IndexError, ValueError)):
        tab[24]
    with pytest.raises((IndexError, ValueError)):
        tab[2, 3, 4]

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_getInput():
    """
    Test the getInput method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test single index access
    assert tab.getInput(0) == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert tab.getInput(23) == {"x": 1.0, "y": 1.0, "z": 1.0}
    
    # Test multi-index access
    assert tab.getInput((0, 0, 0)) == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert tab.getInput((1, 2, 3)) == {"x": 1.0, "y": 1.0, "z": 1.0}
    
    # Test invalid index access
    with pytest.raises((IndexError, ValueError)):
        tab.getInput(24)
    with pytest.raises((IndexError, ValueError)):
        tab.getInput((2, 3, 4))

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_constructor_with_1d_data():
    """
    Test the Tabulation constructor with 1D data.
    """
    data = np.random.rand(24)
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    assert tab.shape == (2, 3, 4)
    assert tab.ndim == 3
    assert tab.size == 24
    assert tab.order == order
    assert np.array_equal(tab.data.flatten(), data)
    for i, key in enumerate(order):
        assert np.array_equal(tab.ranges[key], ranges[key])

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_constructor_invalid_data_shape():
    """
    Test the Tabulation constructor with invalid data shape.
    """
    data = np.random.rand(2, 3)
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    with pytest.raises(ValueError):
        Tabulation(data, ranges, order)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_constructor_invalid_ranges():
    """
    Test the Tabulation constructor with invalid ranges.
    """
    data = np.random.rand(2, 3, 4)
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3)
    }
    order = ["x", "y", "z"]
    
    with pytest.raises(ValueError):
        Tabulation(data, ranges, order)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_constructor_invalid_order():
    """
    Test the Tabulation constructor with invalid order.
    """
    data = np.random.rand(2, 3, 4)
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y"]
    
    with pytest.raises(ValueError):
        Tabulation(data, ranges, order)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_from_pandas():
    """
    Test the Tabulation constructor from a pandas DataFrame.
    """
    
    def f(x, y, z):
        return x*10**2 + y*10**1 + z*10**0
    
    x, y, z = np.meshgrid(np.linspace(0, 1, 2),
                          np.linspace(0, 2, 3),
                          np.linspace(0, 3, 4),
                          indexing="ij")
    data = {
        "x": x.flatten(),
        "y": y.flatten(),
        "z": z.flatten(),
        "output": f(x, y, z).flatten()
    }
    df = DataFrame(data)
    order = ["x", "y", "z"]
    
    tab = Tabulation.from_pandas(df, order, "output")
    
    assert tab.shape == (2, 3, 4)
    assert tab.ndim == 3
    assert tab.size == 24
    assert tab.order == order
    assert np.array_equal(tab.data.flatten(), data["output"])
    for key in order:
        assert np.array_equal(tab.ranges[key], np.unique(data[key]))

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_from_pandas_invalid_dataframe():
    """
    Test the Tabulation constructor from a pandas DataFrame with invalid data.
    """
    data = {
        "x": np.tile(np.linspace(0, 1, 2), 12),
        "y": np.repeat(np.linspace(0, 1, 3), 8),
        "output": np.random.rand(24)
    }
    df = DataFrame(data)
    order = ["x", "y", "z"]
    
    with pytest.raises(ValueError):
        Tabulation.from_pandas(df, order, "output")

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_to_pandas():
    """
    Test the toPandas function to convert a Tabulation to a pandas DataFrame.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    df = toPandas(tab)
    
    assert isinstance(df, DataFrame)
    assert df.shape == (24, 4)
    assert set(df.columns) == {"x", "y", "z", "output"}
    assert np.array_equal(df["output"].values, data.flatten())
    for key in order:
        assert np.array_equal(np.unique(df[key].values), ranges[key])
    #Assert that all combinations of datapoints are present
    assert len(df) == len(df.drop_duplicates(subset=["x", "y", "z"]))

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_order_setter():
    """
    Test the order setter of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Change order
    new_order = ["z", "y", "x"]
    tab.order = new_order
    
    assert tab.order == new_order
    assert tab.shape == (4, 3, 2)
    assert np.array_equal(tab.data, data.transpose(2, 1, 0))
    for i, key in enumerate(new_order):
        assert np.array_equal(tab.ranges[key], ranges[key])
    
    #Assert getitem
    assert tab[0] == 100
    assert tab[(3, 2, 1)] == 223

    #Assert getInput
    assert tab.getInput(0) == {"z": 0.0, "y": 0.0, "x": 0.0}
    assert tab.getInput(23) == {"z": 1.0, "y": 1.0, "x": 1.0}
    
    with pytest.raises(ValueError):
        tab.order = ["x", "y"]
    
    with pytest.raises(ValueError):
        tab.order = ["x", "y", "z", "w"]

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_computeIndex():
    """
    Test the _computeIndex method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test single index access
    assert tab._computeIndex(0) == (0, 0, 0)
    assert tab._computeIndex(23) == (1, 2, 3)
    
    # Test multi-index access
    assert tab._computeIndex([0, 1, 2]) == [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
    
    # Test slice access
    assert tab._computeIndex(slice(0, 3)) == [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
    
    # Test invalid index access
    with pytest.raises(ValueError):
        tab._computeIndex(24)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_setitem():
    """
    Test the __setitem__ method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test single index set
    tab[0] = 999
    assert tab[0] == 999
    
    tab[23] = 888
    assert tab[23] == 888
    
    # Test multi-index set
    tab[0, 0, 0] = 777
    assert tab[0, 0, 0] == 777
    
    tab[1, 2, 3] = 666
    assert tab[1, 2, 3] == 666
    
    # Test slicing set
    tab[0:12] = np.arange(12)
    assert np.array_equal(tab[0:12], np.arange(12))
    
    tab[12:] = np.arange(12, 24)
    assert np.array_equal(tab[12:], np.arange(12, 24))
    
    # Test invalid index set
    with pytest.raises((IndexError, ValueError)):
                tab[24] = 555
    with pytest.raises((IndexError, ValueError)):
                tab[2, 3, 4] = 444

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_slice():
    """
    Test the slice method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 2, 3),
        "z": np.linspace(0, 3, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test slicing with slices
    sliced_tab = tab.slice(slices=[slice(0, 1), slice(0, 2), slice(0, 3)])
    assert sliced_tab.shape == (1, 2, 3)
    assert np.array_equal(sliced_tab.data, data[0:1, 0:2, 0:3])
    
    # Test slicing with ranges
    sliced_tab = tab.slice(ranges={"x": [0.0], "y": [0.0, 1.0], "z": [0.0, 1.0, 2.0]})
    assert sliced_tab.shape == (1, 2, 3)
    assert np.array_equal(sliced_tab.data, data[0:1, 0:2, 0:3])
    
    # Test slicing with keyword arguments
    sliced_tab = tab.slice(x=[0.0], y=[0.0, 1.0], z=[0.0, 1.0, 2.0])
    assert sliced_tab.shape == (1, 2, 3)
    assert np.array_equal(sliced_tab.data, data[0:1, 0:2, 0:3])
    
    # Test slicing with keyword arguments
    sliced_tab = tab.slice(x=[0.0])
    assert sliced_tab.shape == (1, 3, 4)
    assert np.array_equal(sliced_tab.data, data[0:1, :, :])
    
    #Test slicing with single value
    sliced_tab = tab.slice(x=0.0)
    assert sliced_tab.shape == (1, 3, 4)
    assert np.array_equal(sliced_tab.data, data[0:1, :, :])
    
    #Check that all ranges are still ndarray
    for key in sliced_tab.ranges:
        assert isinstance(sliced_tab.ranges[key], np.ndarray)
    
    # Test invalid slicing
    with pytest.raises((ValueError, IndexError)):
        tab.slice(slices=[slice(0, 1), slice(0, 2)])
    with pytest.raises(ValueError):
        tab.slice(ranges={"x": [0.0], "y": [0.0, 0.3]})

    # Test inplace slicing
    tab.slice(slices=[slice(0, 1), slice(0, 2), slice(0, 3)], inplace=True)
    assert tab.shape == (1, 2, 3)
    assert np.array_equal(tab.data, data[0:1, 0:2, 0:3])
    

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_squeeze():
    """
    Test the squeeze method of the Tabulation class.
    """
    data = np.array([[[100], [110], [120]], [[200], [210], [220]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 0, 1)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    squeezed_tab = tab.squeeze(inplace=False)
    
    assert tab != squeezed_tab
    
    assert squeezed_tab.shape == (2, 3)
    assert squeezed_tab.ndim == 2
    assert squeezed_tab.size == 6
    assert squeezed_tab.order == ["x", "y"]
    assert np.array_equal(squeezed_tab.data, data.squeeze())
    for key in squeezed_tab.order:
        assert np.array_equal(squeezed_tab.ranges[key], ranges[key])
        
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_equality():
    """
    Test the equality operator of the Tabulation class.
    """
    data1 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges1 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order1 = ["x", "y", "z"]
    
    tab1 = Tabulation(data1, ranges1, order1)
    
    data2 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges2 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order2 = ["x", "y", "z"]
    
    tab2 = Tabulation(data2, ranges2, order2)
    
    assert tab1 == tab2
    
    data3 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 224]]])  # Different data
    tab3 = Tabulation(data3, ranges2, order2)
    
    assert tab1 != tab3
    
    ranges4 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 2, 4)  # Different ranges
    }
    tab4 = Tabulation(data1, ranges4, order2)
    
    assert tab1 != tab4
    
    order5 = ["z", "x", "y"]  # Different order
    tab5 = tab1.copy()
    tab5.order = order5
    
    assert tab1 != tab5
    
    # Error cases
    with pytest.raises(NotImplementedError):
        tab1 == 1
    with pytest.raises(NotImplementedError):
        "string" == tab1

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_concat():
    """
    Test the concat method of the Tabulation class.
    """
    data1 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges1 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order1 = ["x", "y", "z"]
    
    tab1 = Tabulation(data1, ranges1, order1)
    
    data2 = np.array([[[300, 301, 302, 303],
                       [310, 311, 312, 313],
                       [320, 321, 322, 323]],
                      [[400, 401, 402, 403],
                       [410, 411, 412, 413],
                       [420, 421, 422, 423]]])
    ranges2 = {
        "x": np.linspace(2, 3, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order2 = ["x", "y", "z"]
    
    tab2 = Tabulation(data2, ranges2, order2)
    
    # Test concatenation
    tab_concat = tab1.concat(tab2, inplace=False)
    
    assert tab_concat.shape == (4, 3, 4)
    assert tab_concat.ndim == 3
    assert tab_concat.size == 48
    assert tab_concat.order == order1
    assert np.array_equal(tab_concat.data[:2], data1)
    assert np.array_equal(tab_concat.data[2:], data2)
    
    # Test in-place concatenation
    tab1.concat(tab2, inplace=True)
    
    assert tab1.shape == (4, 3, 4)
    assert tab1.ndim == 3
    assert tab1.size == 48
    assert tab1.order == order1
    assert np.array_equal(tab1.data[:2], data1)
    assert np.array_equal(tab1.data[2:], data2)
    
    # Test concatenation with overlapping regions
    data3 = np.array([[[500, 501, 502, 503],
                       [510, 511, 512, 513],
                       [520, 521, 522, 523]],
                      [[600, 601, 602, 603],
                       [610, 611, 612, 613],
                       [620, 621, 622, 623]]])
    ranges3 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order3 = ["x", "y", "z"]
    
    tab3 = Tabulation(data3, ranges3, order3)
    
    with pytest.raises(ValueError):
        tab1.concat(tab3, inplace=False)
    
    tab_concat = tab1.concat(tab3, inplace=False, overwrite=True)
    
    assert tab_concat.shape == (4, 3, 4)
    assert tab_concat.ndim == 3
    assert tab_concat.size == 48
    assert tab_concat.order == order1
    assert np.array_equal(tab_concat.data[:2], data3)
    assert np.array_equal(tab_concat.data[2:], data2)
    
    #Test concatentation with fill_value
    data4 = [600, 601]
    ranges4 = {
        "x": [0,1],
        "y": [2],
        "z": [1]
    }
    
    tab4 = Tabulation(data4, ranges4, order3)
    
    tab_concat = tab3.concat(tab4, fillValue=0)
    
    assert tab_concat.shape == (2, 4, 4)
    assert tab_concat.ndim == 3
    assert tab_concat.size == 32
    assert tab_concat.order == order1
    assert (tab_concat.slice(y=ranges4["y"],z=set(ranges3["z"]).difference(set(ranges4["z"]))).data == 0).all()
    
    with pytest.raises(ValueError):
        tab3.concat(tab4) #No fill value


#Test concatenation with __add__ and __iadd__
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_add():
    """
    Test the __add__ and __iadd__ methods of the Tabulation class.
    """
    data1 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges1 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order1 = ["x", "y", "z"]
    
    tab1 = Tabulation(data1, ranges1, order1)
    
    data2 = np.array([[[300, 301, 302, 303],
                       [310, 311, 312, 313],
                       [320, 321, 322, 323]],
                      [[400, 401, 402, 403],
                       [410, 411, 412, 413],
                       [420, 421, 422, 423]]])
    ranges2 = {
        "x": np.linspace(2, 3, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order2 = ["x", "y", "z"]
    
    tab2 = Tabulation(data2, ranges2, order2)
    
    tab3 = tab1 + tab2
    assert tab3.shape == (4, 3, 4)
    assert tab3.ndim == 3
    assert tab3.size == 48
    assert tab3.order == order1
    assert np.array_equal(tab3.data[:2], data1)
    assert np.array_equal(tab3.data[2:], data2)
    
    tab1 += tab2
    assert tab1.shape == (4, 3, 4)
    assert tab1.ndim == 3
    assert tab1.size == 48
    assert tab1.order == order1
    assert np.array_equal(tab1.data[:2], data1)
    assert np.array_equal(tab1.data[2:], data2)
    assert tab1 == tab3

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_insertDimension():
    """
    Test the insertDimension method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Insert new dimension
    tab.insertDimension(variable="w", value=0.5, index=1, inplace=True)
    
    assert tab.order == ["x", "w", "y", "z"]
    assert tab.shape == (2, 1, 3, 4)
    assert tab.ndim == 4
    assert tab.size == 24
    assert np.array_equal(tab.ranges["w"], [0.5])
    assert np.array_equal(tab.data, data.reshape(2, 1, 3, 4))
    
    # Test invalid index
    with pytest.raises(ValueError):
        tab.insertDimension(variable="v", value=0.5, index=5, inplace=True)
    
    # Test invalid field type
    with pytest.raises(TypeError):
        tab.insertDimension(variable=123, value=0.5, index=1, inplace=True)
    
    # Test invalid value type
    with pytest.raises(TypeError):
        tab.insertDimension(variable="v", value="invalid", index=1, inplace=True)
    
    # Test invalid index type
    with pytest.raises(TypeError):
        tab.insertDimension(variable="v", value=0.5, index="invalid", inplace=True)
        
    #Test example from documentation
    tab2 = Tabulation(data, ranges, order)
    
    tab3 = tab2.insertDimension(variable="w", value=0.5, index=1, inplace=False)
    tab2.insertDimension(variable="w", value=1.0, index=1, inplace=True)
    tab2.concat(tab, inplace=True)
    
    assert tab2.shape == (2, 2, 3, 4)
    assert tab2.ndim == 4
    assert tab2.size == 48
    assert tab2.order == ["x", "w", "y", "z"]
    assert np.array_equal(tab2.ranges["w"], [0.5, 1.0])
    assert np.array_equal(tab2.data, np.concatenate([data.reshape(2, 1, 3, 4), data.reshape(2, 1, 3, 4)], axis=1))
    
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_plot():
    """
    Test the plot method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test plot method
    ax = tab.plot(x="x", c="z", iso={"y": 0.5})
    
    from matplotlib import pyplot as plt
    ax = plt.subplot()
    ax = tab.plot(x="x", c="y", iso={"z": 1.0}, ax=ax, xlabel="X", ylabel="Y", title="Title", colorMap="viridis")
    
    with pytest.raises(ValueError):
        tab.plot(x="x", c="z", iso={"z": 1.0})
    
    with pytest.raises(ValueError):
        tab.plot(x="y", c="z", iso={"x": 0.5})
    
    # Test plotting with equivalent keyword arguments
    ax = tab.plot(x="x", c="z", iso={"y": 0.5}, xLabel="X", yLabel="Y", cmap="viridis")
    with pytest.raises(ValueError):
        tab.plot(x="x", c="z", iso={"y": 0.5}, xLabel="X", yLabel="Y", cmap="viridis", xlabel="viridis")
    
    #Plot a table with only two axes (empty iso)
    tab = tab.slice(z=[0.0]).squeeze()
    ax = tab.plot(x="x", c="y", xLabel="X", yLabel="Y", cmap="viridis")
    with pytest.raises(ValueError):
        ax = tab.plot(x="x", c="z", xLabel="X", yLabel="Y", cmap="viridis")

def test_tabulation_plotHeatmap():
    """
    Test the plot method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test plot method
    ax = tab.plotHeatmap(x="x", y="z", iso={"y": 0.5})
    
    from matplotlib import pyplot as plt
    ax = plt.subplot()
    ax = tab.plot(x="x", c="y", iso={"z": 1.0}, ax=ax, xlabel="X", ylabel="Y", title="Title", colorMap="viridis")
    
    with pytest.raises(ValueError):
        tab.plotHeatmap(x="x", y="z", iso={"z": 1.0})
    
    with pytest.raises(ValueError):
        tab.plotHeatmap(x="y", y="z", iso={"x": 0.5})
    
    # Test plotting with equivalent keyword arguments
    ax = tab.plotHeatmap(x="x", y="z", iso={"y": 0.5}, xLabel="X", yLabel="Y", cmap="viridis")
    with pytest.raises(ValueError):
        tab.plotHeatmap(x="x", y="z", iso={"y": 0.5}, xLabel="X", yLabel="Y", cmap="viridis", xlabel="viridis")
    
    #Plot a table with only two axes (empty iso)
    tab = tab.slice(z=[0.0]).squeeze()
    ax = tab.plotHeatmap(x="x", y="y", xLabel="X", yLabel="Y", cmap="viridis")
    with pytest.raises(ValueError):
        ax = tab.plotHeatmap(x="x", y="z", xLabel="X", yLabel="Y", cmap="viridis")
    
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_interpolation():
    """
    Test the interpolation (__call__) method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    # Test interpolation at known points
    assert tab(0.0, 0.0, 0.0) == 100
    assert tab(1.0, 1.0, 1.0) == 223
    assert tab(1.0, 1.0, 0.0) == 220
    
    # Test interpolation at midpoints
    assert np.isclose(tab(0.5, 0.5, 0.5), 161.5)
    assert np.isclose(tab(0.5, 0.5, 0.0), 160.0)
    
    # Test interpolation with out-of-bounds method
    assert np.isnan(tab(1.5, 1.5, 1.5, outOfBounds="nan"))
    assert tab(1.5, 1.5, 1.5, outOfBounds="extrapolate") > 223
    
    with pytest.raises(ValueError):
        tab(1.5, 1.5, 1.5, outOfBounds="fatal")
    
    # Test invalid number of arguments
    with pytest.raises(ValueError):
        tab(0.0, 0.0)
    with pytest.raises(ValueError):
        tab(0.0, 0.0, 0.0, 0.0)
    
    #Interpolation with multiple points
    assert np.array_equal(tab((0,0,0), (1,1,1)), np.array([100, 223]))
    out = tab((0,0,0), (1,1,2), outOfBounds="nan")
    assert np.isnan(out[1])
    assert np.array_equal(out[0], 100)
    
    #Interpolation with a field that has a single value
    tab2 = tab.slice(z=[0.0])
    assert np.array_equal(tab2(0.0, 0.0, 0.0), 100)
    with pytest.warns(TabulationAccessWarning):
        assert np.array_equal(tab2(0.0, 0.0, 2.0), 100)
    
    #Interpolation with a field that has a single value and multiple points
    assert np.array_equal(tab2((0,0,0), (1,1,0)), np.array([100, 220]))
    with pytest.warns(TabulationAccessWarning):
        assert np.array_equal(tab2((0,0,0), (1,1,1)), np.array([100, 220]))
        
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_interpolator_property():
    """
    Test the interpolator property of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    
    interpolator = tab.interpolator
    from scipy.interpolate import RegularGridInterpolator
    assert isinstance(interpolator, RegularGridInterpolator)
    assert np.isclose(interpolator((0.5, 0.5, 0.5)), 161.5)
    assert np.isclose(interpolator((0.5, 0.5, 0.0)), 160.0)
    
    # Test interpolator with out-of-bounds method
    tab.outOfBounds = "nan"
    assert interpolator is not tab.interpolator
    interpolator = tab.interpolator
    assert np.isnan(interpolator((1.5, 1.5, 1.5)))
    
    tab.outOfBounds = "extrapolate"
    assert interpolator is not tab.interpolator
    interpolator = tab.interpolator
    assert interpolator((1.5, 1.5, 1.5)) > 223
    
    tab.outOfBounds = "fatal"
    assert interpolator is not tab.interpolator
    interpolator = tab.interpolator
    with pytest.raises(ValueError):
        interpolator((1.5, 1.5, 1.5))

    #Test changing the data
    tab[:] = tab[:] + 1
    assert interpolator is not tab.interpolator
    interpolator = tab.interpolator
    assert np.isclose(interpolator((0.5, 0.5, 0.5)), 162.5)
    assert np.isclose(interpolator((0.5, 0.5, 0.0)), 161.0)

@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_concat_function():
    """
    Test the concat function for merging multiple Tabulation instances.
    """
    data1 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges1 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order1 = ["x", "y", "z"]
    
    tab1 = Tabulation(data1, ranges1, order1)
    
    data2 = np.array([[[300, 301, 302, 303],
                       [310, 311, 312, 313],
                       [320, 321, 322, 323]],
                      [[400, 401, 402, 403],
                       [410, 411, 412, 413],
                       [420, 421, 422, 423]]])
    ranges2 = {
        "x": np.linspace(2, 3, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order2 = ["x", "y", "z"]
    
    tab2 = Tabulation(data2, ranges2, order2)
    
    data3 = np.array([[[500, 501, 502, 503],
                       [510, 511, 512, 513],
                       [520, 521, 522, 523]],
                      [[600, 601, 602, 603],
                       [610, 611, 612, 613],
                       [620, 621, 622, 623]]])
    ranges3 = {
        "x": np.linspace(4, 5, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order3 = ["x", "y", "z"]
    
    tab3 = Tabulation(data3, ranges3, order3)
    
    # Test concatenation of multiple tables
    tab_concat = concat(tab1, tab2, tab3)
    
    assert tab_concat.shape == (6, 3, 4)
    assert tab_concat.ndim == 3
    assert tab_concat.size == 72
    assert tab_concat.order == order1
    assert np.array_equal(tab_concat.data[:2], data1)
    assert np.array_equal(tab_concat.data[2:4], data2)
    assert np.array_equal(tab_concat.data[4:], data3)
    
    #Check that the original tables are not modified
    assert tab1.shape == (2, 3, 4)
    assert tab2.shape == (2, 3, 4)
    assert tab3.shape == (2, 3, 4)
    assert tab1.order == order1
    assert tab2.order == order2
    assert tab3.order == order3
    assert np.array_equal(tab1.data, data1)
    assert np.array_equal(tab2.data, data2)
    assert np.array_equal(tab3.data, data3)
    
    #Concatenation with table with different order
    tab2.order = ["z", "x", "y"]
    tab_concat2 = concat(tab1, tab2, tab3)
    
    assert tab_concat2.shape == tab_concat.shape
    assert tab_concat2.ndim == tab_concat.ndim
    assert tab_concat2.size == tab_concat.size
    assert tab_concat2.order == order1
    assert np.array_equal(tab_concat2.data, tab_concat.data)

def test_Tabulation_str_repr():
    data1 = np.array([[[100, 101, 102, 103],
                       [110, 111, 112, 113],
                       [120, 121, 122, 123]],
                      [[200, 201, 202, 203],
                       [210, 211, 212, 213],
                       [220, 221, 222, 223]]])
    ranges1 = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order1 = ["x", "y", "z"]
    
    tab1 = Tabulation(data1, ranges1, order1)
    
    print(tab1)
    print(repr(tab1))
    
@pytest.mark.filterwarnings("error::libICEpost.src.base.dataStructures.Tabulation.Tabulation.TabulationAccessWarning")
def test_tabulation_copy():
    """
    Test the copy method of the Tabulation class.
    """
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    tab_copy = tab.copy()
    
    assert tab == tab_copy
    assert tab is not tab_copy
    assert tab._data is not tab_copy._data
    assert tab._interpolator is not tab_copy._interpolator
    assert tab._order is not tab_copy._order
    assert tab._ranges is not tab_copy._ranges
    
    #Check the types
    assert isinstance(tab_copy, Tabulation)
    assert isinstance(tab_copy.data, np.ndarray)
    assert isinstance(tab_copy.ranges, dict)
    assert isinstance(tab_copy.order, list)
    for r in tab_copy.ranges.values():
        assert isinstance(r, np.ndarray)
    for o in tab_copy.order:
        assert isinstance(o, str)
    
    # Modify the copy and ensure the original is not affected
    tab_copy[0] = 999
    assert tab[0] != 999
    assert tab_copy[0] == 999
    
    tab_copy.order = ["z", "y", "x"]
    assert tab.order != tab_copy.order
    assert tab_copy.order == ["z", "y", "x"]

def test_tabulation_setRange():
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": np.linspace(0, 1, 2),
        "y": np.linspace(0, 1, 3),
        "z": np.linspace(0, 1, 4)
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    tab.setRange("x", [0, 2])
    
    assert np.array_equal(tab.ranges["x"], [0, 2])
    assert isinstance(tab.ranges["x"], np.ndarray)
    assert tab(2,0,0) == 200
    
    with pytest.raises(ValueError):
        tab.setRange("x", [0, 1, 2])
    with pytest.raises(ValueError):
        tab.setRange("x", [0, 0])
    with pytest.raises(ValueError):
        tab.setRange("x", [2, 0])
    with pytest.raises(ValueError):
        tab.setRange("k", [0, 2])

def test_tabulation_clip():
    data = np.array([[[100, 101, 102, 103],
                      [110, 111, 112, 113],
                      [120, 121, 122, 123]],
                     [[200, 201, 202, 203],
                      [210, 211, 212, 213],
                      [220, 221, 222, 223]]])
    ranges = {
        "x": [0, 1],
        "y": [0, 1, 2],
        "z": [0, 1, 2, 3]
    }
    order = ["x", "y", "z"]
    
    tab = Tabulation(data, ranges, order)
    
    #Key word arguments
    tab_clip = tab.clip(y=(1,2))
    assert tab_clip.shape == (2, 2, 4)
    assert np.array_equal(tab_clip.data, data[:,1:3,:])
    assert np.array_equal(tab_clip.ranges["y"], np.array([1,2]))
    
    #Both
    tab_clip = tab.clip(x=(0,1), ranges={"y": (1,2)})
    assert tab_clip.shape == (2, 2, 4)
    assert np.array_equal(tab_clip.data, data[:,1:3,:])
    assert np.array_equal(tab_clip.ranges["y"], np.array([1,2]))
    assert np.array_equal(tab_clip.ranges["x"], np.array([0,1]))
    
    #None
    tab_clip = tab.clip(z=(None, 2))
    assert tab_clip.shape == (2, 3, 3)
    assert np.array_equal(tab_clip.data, data[:,:,0:3])
    assert np.array_equal(tab_clip.ranges["z"], np.array([0,1,2]))
    
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
    tab.clip(y=(-5,1), inplace=True)
    assert tab.shape == (2, 2, 4)
    assert np.array_equal(tab.data, data[:,0:2,:])
    assert np.array_equal(tab.ranges["y"], np.array([0,1]))