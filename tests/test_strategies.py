from hypothesis_csv.strategies import data_rows
from hypothesis import strategies as st
from hypothesis import settings, given


@settings(use_coverage=False)
@given(data=st.data(),lines_num=st.integers(min_value=0, max_value=200))
def test_data_rows_fixed_lines_num(data,lines_num):
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
    assert all([len(r) >=1 for r in rows])


@settings(use_coverage=False)
@given(data=st.data(),columns_num=st.integers(min_value=1, max_value=10))
def test_data_rows_fixed_column_num(data,columns_num):
    rows = data.draw(data_rows(columns=columns_num))
    assert len(rows) >= 1
    assert all([len(r) == columns_num and all([type(field) in [int,str,float]] for field in r) for r in rows])