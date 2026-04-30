import pytest
from libICEpost.src.base.dataStructures._loading import (
    load_file, load_array, load_uniform, load_function, load_calculated,
    load_files, load_stitched, load_conditional, loadField, LoadingMethod,
    FieldDependencyError,
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
        load_file(timeseries, fileName=temp_file_path, field=fieldName, verbose=True)
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
        loadField(timeseries, field=fieldName, method="file", fileName=temp_file_path, verbose=True)
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


# ─────────────────────────────────────────────────────────────────────────────
# load_files tests
# ─────────────────────────────────────────────────────────────────────────────

def test_load_files_basic(tmp_path):
    """3 sequential files are merged into a single continuous field."""
    f1 = tmp_path / "f1.dat"
    f2 = tmp_path / "f2.dat"
    f3 = tmp_path / "f3.dat"
    f1.write_text("0.0 10.0\n1.0 20.0\n2.0 30.0\n")
    f2.write_text("3.0 40.0\n4.0 50.0\n5.0 60.0\n")
    f3.write_text("6.0 70.0\n7.0 80.0\n8.0 90.0\n")

    ts = TimeSeries()
    load_files(ts, "v", files=[str(f1), str(f2), str(f3)], verbose=False)

    assert "v" in ts.columns
    assert ts[ts.timeName].tolist() == pytest.approx(list(range(9)))
    assert ts["v"].tolist() == pytest.approx([10, 20, 30, 40, 50, 60, 70, 80, 90])


def test_load_files_glob_pattern(tmp_path):
    """Glob pattern expands to the correct set of files."""
    (tmp_path / "data_01.dat").write_text("0.0 1.0\n1.0 2.0\n")
    (tmp_path / "data_02.dat").write_text("2.0 3.0\n3.0 4.0\n")
    (tmp_path / "other.dat").write_text("99.0 99.0\n")  # must NOT be picked up

    ts = TimeSeries()
    load_files(ts, "v", files=str(tmp_path / "data_*.dat"), verbose=False)

    assert ts[ts.timeName].tolist() == pytest.approx([0.0, 1.0, 2.0, 3.0])
    assert ts["v"].tolist() == pytest.approx([1.0, 2.0, 3.0, 4.0])


def test_load_files_list_of_patterns(tmp_path):
    """List of glob patterns resolves to the union (no duplicates)."""
    sub_a = tmp_path / "a"
    sub_b = tmp_path / "b"
    sub_a.mkdir()
    sub_b.mkdir()
    (sub_a / "run.dat").write_text("0.0 1.0\n1.0 2.0\n")
    (sub_b / "run.dat").write_text("2.0 3.0\n3.0 4.0\n")

    ts = TimeSeries()
    load_files(ts, "v",
               files=[str(sub_a / "run.dat"), str(sub_b / "run.dat")],
               verbose=False)

    assert ts[ts.timeName].tolist() == pytest.approx([0.0, 1.0, 2.0, 3.0])
    assert ts["v"].tolist() == pytest.approx([1.0, 2.0, 3.0, 4.0])


def test_load_files_single_file(tmp_path):
    """Single file: no stitching, result identical to load_file."""
    f = tmp_path / "single.dat"
    f.write_text("0.0 5.0\n1.0 6.0\n2.0 7.0\n")

    ts_files = TimeSeries()
    load_files(ts_files, "v", files=str(f), verbose=False)

    ts_file = TimeSeries()
    load_file(ts_file, "v", str(f), verbose=False)

    assert ts_files["v"].tolist() == pytest.approx(ts_file["v"].tolist())
    assert ts_files[ts_files.timeName].tolist() == pytest.approx(ts_file[ts_file.timeName].tolist())


def test_load_files_conflict_same_start(tmp_path):
    """When two files share the same start time, the longer one is kept and a warning emitted."""
    short = tmp_path / "short.dat"
    long_ = tmp_path / "long.dat"
    short.write_text("0.0 1.0\n5.0 2.0\n")        # [0, 5]
    long_.write_text("0.0 10.0\n5.0 20.0\n10.0 30.0\n")  # [0, 10]

    ts = TimeSeries()
    with pytest.warns(RuntimeWarning, match="shares start time"):
        load_files(ts, "v", files=[str(short), str(long_)], verbose=False)

    # Only the longer file's data should be present
    assert ts[ts.timeName].tolist() == pytest.approx([0.0, 5.0, 10.0])
    assert ts["v"].tolist() == pytest.approx([10.0, 20.0, 30.0])


def test_load_files_per_file_kwargs_regex(tmp_path):
    """Per-file regex kwargs (y_scale) are applied independently to each file."""
    f1 = tmp_path / "scale10.dat"
    f2 = tmp_path / "scale100.dat"
    f1.write_text("0.0 1.0\n1.0 2.0\n2.0 3.0\n")
    f2.write_text("3.0 4.0\n4.0 5.0\n5.0 6.0\n")

    ts = TimeSeries()
    load_files(ts, "v",
               files=[str(f1), str(f2)],
               per_file_kwargs={
                   r"scale10\.dat": {"y_scale": 10.0},
                   r"scale100\.dat": {"y_scale": 100.0},
               },
               verbose=False)

    assert ts["v"].tolist() == pytest.approx([10.0, 20.0, 30.0, 400.0, 500.0, 600.0])


def test_load_files_x_off_sorting(tmp_path):
    """Sorting uses transformed times (after x_off), not raw times."""
    # Raw times: "a_file" has [10, 20], "b_file" has [0, 10].
    # Raw sort: b_file first, a_file second.
    # Per-file x_off: a_file x_off=-10 → transformed [0, 10]; b_file x_off=+10 → transformed [10, 20].
    # Transformed sort: a_file first, b_file second.
    fa = tmp_path / "a_file.dat"
    fb = tmp_path / "b_file.dat"
    fa.write_text("10.0 1.0\n20.0 1.0\n")   # values all 1.0
    fb.write_text("0.0  2.0\n10.0 2.0\n")   # values all 2.0

    ts = TimeSeries()
    load_files(ts, "v",
               files=[str(fa), str(fb)],
               per_file_kwargs={
                   r"a_file": {"x_off": -10.0},
                   r"b_file": {"x_off": 10.0},
               },
               verbose=False)

    # Transformed order: a_file [0→10] first, b_file [10→20] second.
    # Stitching: a_file until b_file starts (t=10), then b_file.
    # Expected: t=[0,10,20], v=[1.0, 2.0, 2.0]
    assert ts[ts.timeName].tolist() == pytest.approx([0.0, 10.0, 20.0])
    assert ts["v"].tolist() == pytest.approx([1.0, 2.0, 2.0])


def test_load_files_no_match(tmp_path):
    """Glob pattern that matches nothing raises ValueError."""
    ts = TimeSeries()
    with pytest.raises(ValueError, match="No files found"):
        load_files(ts, "v", files=str(tmp_path / "nonexistent_*.dat"), verbose=False)


def test_load_files_empty_file(tmp_path):
    """File with no data rows raises ValueError."""
    f = tmp_path / "empty.dat"
    f.write_text("# only a comment, no data\n")

    ts = TimeSeries()
    with pytest.raises((ValueError, Exception)):
        load_files(ts, "v", files=str(f), verbose=False)


def test_load_files_original_ts_unchanged_on_error(tmp_path):
    """If loading fails mid-way, the original TimeSeries is left unmodified."""
    f1 = tmp_path / "good.dat"
    f2 = tmp_path / "bad.dat"
    f1.write_text("0.0 10.0\n1.0 20.0\n")
    f2.write_text("2.0 30.0\n3.0 not_a_number\n")  # bad y-column value

    ts = TimeSeries()
    ts.loadArray([[0.0, 1.0], [100.0, 200.0]], "existing", dataFormat="row")
    original_columns = list(ts.columns)

    with pytest.raises(Exception):
        load_files(ts, "new_field", files=[str(f1), str(f2)], verbose=False)

    assert "new_field" not in ts.columns
    assert list(ts.columns) == original_columns


def test_load_files_invalid_per_file_kwargs_regex(tmp_path):
    """Invalid regex pattern in per_file_kwargs raises ValueError before any loading."""
    f = tmp_path / "f.dat"
    f.write_text("0.0 1.0\n1.0 2.0\n")

    ts = TimeSeries()
    with pytest.raises(ValueError, match="not a valid regex"):
        load_files(ts, "v", files=str(f),
                   per_file_kwargs={"[invalid_regex": {"y_scale": 2.0}},
                   verbose=False)


def test_loadField_files_method(tmp_path):
    """Integration test: loadField dispatches to load_files correctly."""
    f1 = tmp_path / "p1.dat"
    f2 = tmp_path / "p2.dat"
    f1.write_text("0.0 1.0\n1.0 2.0\n")
    f2.write_text("2.0 3.0\n3.0 4.0\n")

    ts = TimeSeries()
    loadField(ts, field="v", method="files",
              files=[str(f1), str(f2)], verbose=False)

    assert "v" in ts.columns
    assert ts["v"].tolist() == pytest.approx([1.0, 2.0, 3.0, 4.0])


# ─────────────────────────────────────────────────────────────────────────────
# load_conditional tests
# ─────────────────────────────────────────────────────────────────────────────

def _make_ts(*name_data_pairs):
    """Helper: build a TimeSeries with time=[0,1,2,3] and the given (name, values) columns."""
    ts = TimeSeries()
    time = [0.0, 1.0, 2.0, 3.0]
    ts.loadArray([time, time], varName="dummy_init", dataFormat="row", verbose=False)
    del ts["dummy_init"]
    for name, values in name_data_pairs:
        ts.loadArray([time, list(values)], varName=name, dataFormat="row", verbose=False)
    return ts


def test_load_conditional_gt_fields():
    """F1 > F2 → element-wise maximum of the two fields."""
    ts = _make_ts(("a", [1.0, 5.0, 3.0, 2.0]),
                  ("b", [4.0, 2.0, 3.0, 6.0]))
    load_conditional(ts, "res", f1="a", operator=">", f2="b", verbose=False)
    assert ts["res"].tolist() == pytest.approx([4.0, 5.0, 3.0, 6.0])


def test_load_conditional_lt_fields():
    """F1 < F2 → element-wise minimum of the two fields."""
    ts = _make_ts(("a", [1.0, 5.0, 3.0, 2.0]),
                  ("b", [4.0, 2.0, 3.0, 6.0]))
    load_conditional(ts, "res", f1="a", operator="<", f2="b", verbose=False)
    assert ts["res"].tolist() == pytest.approx([1.0, 2.0, 3.0, 2.0])


def test_load_conditional_constant_f2():
    """F1 > constant → clip field from below (F2 is a scalar)."""
    ts = _make_ts(("p", [1.0, 6.0, 4.0, 2.0]))
    load_conditional(ts, "p_clip", f1="p", operator=">", f2=3.0, verbose=False)
    # where p > 3 use p, else use 3.0
    assert ts["p_clip"].tolist() == pytest.approx([3.0, 6.0, 4.0, 3.0])


def test_load_conditional_constant_f1():
    """Constant true-branch: result is K where condition holds, else F2."""
    ts = _make_ts(("p", [1.0, 6.0, 4.0, 2.0]))
    load_conditional(ts, "res", f1=10.0, operator="<", f2="p", verbose=False)
    # f3=f1=10.0, f4=f2=p: condition = 10.0 < p[t]
    # t=0: 10<1 False → p=1; t=1: 10<6 False → 6; t=2: 10<4 False → 4; t=3: 10<2 False → 2
    assert ts["res"].tolist() == pytest.approx([1.0, 6.0, 4.0, 2.0])


def test_load_conditional_custom_f3_f4():
    """(F3 >= F4) ? F1 : F2 with all four operands distinct."""
    ts = _make_ts(("f1", [10.0, 10.0, 10.0, 10.0]),
                  ("f2", [20.0, 20.0, 20.0, 20.0]),
                  ("f3", [5.0,  8.0,  3.0,  9.0]),
                  ("f4", [6.0,  7.0,  4.0,  9.0]))
    load_conditional(ts, "res", f1="f1", operator=">=", f2="f2",
                     f3="f3", f4="f4", verbose=False)
    # condition: f3 >= f4 → [F, T, F, T]
    # result:    [20, 10, 20, 10]
    assert ts["res"].tolist() == pytest.approx([20.0, 10.0, 20.0, 10.0])


def test_load_conditional_eq_tolerance():
    """== operator uses np.isclose with configurable rel_tol."""
    ts = _make_ts(("a", [1.0, 1.0 + 1e-7, 1.0 + 1e-4, 2.0]),
                  ("b", [1.0, 1.0,         1.0,         2.0]))
    # With default rel_tol=1e-6: first two pairs equal, third not
    load_conditional(ts, "res", f1="a", operator="==", f2="b", verbose=False)
    # t=0: equal → a=1.0; t=1: |1e-7/1| < 1e-6 → equal → a≈1.0
    # t=2: |1e-4/1| > 1e-6 → not equal → b=1.0; t=3: equal → a=2.0
    assert ts["res"].tolist() == pytest.approx([1.0, 1.0 + 1e-7, 1.0, 2.0])


def test_load_conditional_neq_tolerance():
    """!= operator returns F1 where values differ, F2 where equal (within tolerance)."""
    ts = _make_ts(("a", [1.0, 2.0,          1.0, 4.0]),
                  ("b", [1.0, 2.0 + 1e-4,   1.0, 4.0]))
    # rel_tol=1e-6 (default):
    # t=0,2,3: a==b exactly → condition False → result=b
    # t=1: |1e-4| >> rtol*2 → a != b → condition True → result=a=2.0
    load_conditional(ts, "res", f1="a", operator="!=", f2="b", verbose=False)
    assert ts["res"].tolist() == pytest.approx([1.0, 2.0, 1.0, 4.0])


def test_load_conditional_isnan():
    """isnan(F3) selects F1 where F3 is NaN, F2 otherwise."""
    import math
    nan = float("nan")
    ts = _make_ts(("raw",    [1.0, nan, 3.0, nan]),
                  ("backup", [10.0, 20.0, 30.0, 40.0]))
    load_conditional(ts, "clean", f1="backup", operator="isnan", f2="raw",
                     f3="raw", verbose=False)
    # where raw is NaN → backup; else → raw
    result = ts["clean"].tolist()
    assert result[0] == pytest.approx(1.0)   # raw is valid
    assert result[1] == pytest.approx(20.0)  # raw is NaN → backup
    assert result[2] == pytest.approx(3.0)   # raw is valid
    assert result[3] == pytest.approx(40.0)  # raw is NaN → backup


def test_load_conditional_missing_field():
    """Any operand referencing a non-existent field raises FieldDependencyError."""
    ts = _make_ts(("a", [1.0, 2.0, 3.0, 4.0]))
    with pytest.raises(FieldDependencyError):
        load_conditional(ts, "res", f1="a", operator=">", f2="nonexistent", verbose=False)
    with pytest.raises(FieldDependencyError):
        load_conditional(ts, "res", f1="nonexistent", operator=">", f2="a", verbose=False)
    with pytest.raises(FieldDependencyError):
        load_conditional(ts, "res", f1="a", operator=">", f2=0.0,
                         f3="nonexistent", verbose=False)


def test_load_conditional_invalid_operator():
    """Unrecognised operator string raises ValueError."""
    ts = _make_ts(("a", [1.0, 2.0, 3.0, 4.0]))
    with pytest.raises(ValueError):
        load_conditional(ts, "res", f1="a", operator="???", f2="a", verbose=False)


def test_load_conditional_empty_ts():
    """Empty TimeSeries raises FieldDependencyError."""
    ts = TimeSeries()
    with pytest.raises(FieldDependencyError):
        load_conditional(ts, "res", f1=1.0, operator=">", f2=0.0, verbose=False)


def test_loadField_conditional_method():
    """Integration: loadField dispatches to load_conditional correctly."""
    ts = _make_ts(("a", [1.0, 5.0, 3.0, 2.0]),
                  ("b", [4.0, 2.0, 3.0, 6.0]))
    loadField(ts, field="res", method="conditional",
              f1="a", operator=">", f2="b", verbose=False)
    assert ts["res"].tolist() == pytest.approx([4.0, 5.0, 3.0, 6.0])


def test_loadField_cond_alias():
    """Alias method='cond' works identically to 'conditional'."""
    ts = _make_ts(("a", [1.0, 5.0, 3.0, 2.0]),
                  ("b", [4.0, 2.0, 3.0, 6.0]))
    loadField(ts, field="res", method="cond",
              f1="a", operator=">", f2="b", verbose=False)
    assert ts["res"].tolist() == pytest.approx([4.0, 5.0, 3.0, 6.0])