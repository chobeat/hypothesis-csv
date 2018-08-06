from csv import DictWriter, list_dialects
from io import StringIO

from hypothesis.strategies import lists

from hypothesis_csv._data_rows import *
from hypothesis_csv.type_utils import *


def _records_to_csv(data, dialect, has_header=True):
    f = StringIO()
    w = DictWriter(f, dialect=dialect, fieldnames=data[0].keys())
    if has_header:
        w.writeheader()
    for row in data:
        w.writerow(row)

    return f.getvalue()


def draw_header(draw, header_len):
    return draw(lists(text(min_size=1,
                           alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
                      min_size=header_len, max_size=header_len, unique=True))


def draw_dialect(draw):
    return draw(sampled_from(list_dialects()))


@overload
def _get_header_and_column_types(draw, header, columns):
    raise InvalidArgument("Header or column are of invalid type")


@overload
def _get_header_and_column_types(draw, header: is_seq, columns: is_seq):
    if len(header) == len(columns):
        return header, columns
    else:
        raise InvalidArgument("Header and columns must be of the same size")


@overload
def _get_header_and_column_types(draw, header: is_seq,
                                 columns: is_none):
    return header, len(header)


@overload
def _get_header_and_column_types(draw, header: is_none, columns: is_none):
    columns = draw(integers(min_value=1, max_value=10))
    return None, columns


@overload
def _get_header_and_column_types(draw, header: isa(int), columns: isa(int)):
    if header == columns:

        header_fields = draw_header(draw, header)

        return header_fields, len(header_fields)
    else:
        raise InvalidArgument("Header and columns must be of the same size")


@overload
def _get_header_and_column_types(draw, header: is_none, columns: isa(int)):
    return None, columns


@overload
def _get_header_and_column_types(draw, header: isa(int), columns: is_none):
    return _get_header_and_column_types(draw, header, header)


@overload
def _get_header_and_column_types(draw, header: is_none, columns: is_seq):
    return None, columns


@composite
def csv(draw, header=None, columns=None, lines=None, dialect="excel"):
    """
    Strategy to produce a CSV string. Uses `data_rows` strategy to generate the values. Refer to the `data_rows`
    strategy for more details about the `columns` and `lines` parameter.

    :param draw:
    :param header: if a list of strings, these will be used as the header for each column, according to their position.
    If an int, this parameter will define the number of columns to be used. If None, the produced CSV will have no
     header
    :param columns: If a list of strategies, these will be used to draw the values for each column.
    If an int, this parameter will define the number of columns to be used. If not provided the number of columns will
    be drawn randomly or the `header` param will be used.
    :param lines: number of rows in the CSV.
    :param dialect: specify the CSV dialect to use. Based on the dialects available in the standard
    python library's `csv'. Default is "excel". If set to None, the dialect is randomly drawn from all the available
    dialects.
    :return: a string in CSV format
    """
    header_param, columns = _get_header_and_column_types(draw, header, columns)
    rows = list(draw(data_rows(lines=lines, columns=columns)))
    dialect = dialect or draw_dialect(draw)
    header = header_param or ["col_{}".format(i) for i in range(len(rows[0]))]  # placeholder header for DictWriter

    data = [dict(zip(header, d)) for d in rows]

    return _records_to_csv(data, has_header=header_param is not None, dialect=dialect)
