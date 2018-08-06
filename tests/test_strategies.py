import string
from io import StringIO

import pytest
from hypothesis import settings, given
from hypothesis import strategies as st
from hypothesis.errors import InvalidArgument
from meza.io import read_csv
from meza.process import detect_types

from hypothesis_csv.strategies import data_rows, csv


def csv2records(string, has_header=True, delimiter=","):
    return list(read_csv(StringIO(string), has_header=has_header, delimiter=delimiter))


@settings(use_coverage=False)
@given(data=st.data(), lines_num=st.integers(min_value=0, max_value=200))
def test_data_rows_fixed_lines_num(data, lines_num):
    rows = data.draw(data_rows(lines=lines_num, columns=[st.integers(), st.integers(), st.floats()]))
    assert len(rows) == lines_num
    assert all([len(r) == 3 for r in rows])


@settings(use_coverage=False)
@given(data=st.data())
def test_data_rows_random_lines_num(data):
    rows = data.draw(data_rows(columns=[st.integers(), st.integers(), st.floats()]))
    assert len(rows) >= 1
    assert all([len(r) == 3 for r in rows])


@settings(use_coverage=False)
@given(data=st.data())
def test_data_rows_all_random(data):
    rows = data.draw(data_rows())
    assert len(rows) >= 1
    assert all([len(r) >= 1 for r in rows])


@settings(use_coverage=False)
@given(data=st.data(), columns_num=st.integers(min_value=1, max_value=10))
def test_data_rows_fixed_column_num(data, columns_num):
    rows = data.draw(data_rows(columns=columns_num))
    assert len(rows) >= 1
    assert all([len(r) == columns_num and all([type(field) in [int, str, float]] for field in r) for r in rows])


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_all_random(data):
    csv_string = data.draw(csv())

    assert isinstance(csv_string, str)


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_header_simple(data):
    header = ["abc", "cde"]
    csv_string = data.draw(csv(header=header, lines=5))
    records = csv2records(csv_string)

    extracted_header = list(records[0].keys())
    assert extracted_header == header


@settings(use_coverage=False)
@given(data=st.data(), header=st.lists(st.text(min_size=1, max_size=5,
                                               alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
                                       min_size=1, max_size=5))
def test_csv_header_property(data, header):
    header = list(set(header))
    csv_string = data.draw(csv(header=header))
    records = csv2records(csv_string)
    extracted_header = list(records[0].keys())
    assert extracted_header == header


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_lines_fixed(data):
    lines = 10
    csv_string = data.draw(csv(lines=lines))
    records = csv2records(csv_string, has_header=False)
    assert len(records) == lines


@pytest.mark.parametrize("kwargs", [{"columns": "xyz"}, {"lines": "xyz"}])
@given(data=st.data())
def test_csv_parameter_fail(data, kwargs):
    with pytest.raises(InvalidArgument):
        data.draw(csv(**kwargs))


@pytest.mark.parametrize("kwargs", [{"header": 5}, {"columns": 3}])
@given(data=st.data())
def test_csv_header_int(data, kwargs):
    csv_string = data.draw(csv(**kwargs))
    records = csv2records(csv_string, has_header="header" in kwargs)
    extracted_header = list(records[0].keys())
    assert len(extracted_header) == list(kwargs.values())[0]


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_columns_seq(data):
    columns = [
        st.text(min_size=1, max_size=100, alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
        st.integers(), st.floats(min_value=1.2, max_value=100.12)]

    csv_string = data.draw(csv(columns=columns, lines=40))
    records = csv2records(csv_string, has_header=False)
    detected_types = detect_types(records)[1]
    types = list(map(lambda x: x["type"], detected_types["types"]))
    assert len(records) == 40
    assert types == ["text", "int", "float"]


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_columns_and_header_seq(data):
    columns = [
        st.text(min_size=1, max_size=100, alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
        st.integers(), st.floats(min_value=1.2, max_value=100.12)]
    header = ["x", "y", "z"]
    csv_string = data.draw(csv(header=header, columns=columns, lines=10))
    records = csv2records(csv_string)
    detected_types = detect_types(records)[1]
    types = list(map(lambda x: x["type"], detected_types["types"]))

    assert types == ["text", "int", "float"]

    extracted_header = list(records[0].keys())
    assert extracted_header == header


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_dialect_tab(data):
    header = ["abc", "cde"]
    csv_string = data.draw(csv(header=header, lines=5, dialect="excel-tab"))
    records = csv2records(csv_string, delimiter="\t")

    extracted_header = list(records[0].keys())
    assert extracted_header == header
    assert len(records) == 5


@settings(use_coverage=False)
@given(data=st.data())
def test_csv_dialect_none(data):
    header = ["abc", "cde"]
    csv_string = data.draw(csv(header=header, lines=5, dialect=None))
    records = csv2records(csv_string)

    assert len(records) == 5
