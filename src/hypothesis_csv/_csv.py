from hypothesis.strategies import lists
from meza.convert import records2csv

from hypothesis_csv._data_rows import *
from hypothesis_csv.type_utils import *


def draw_header(draw, header_len):
    return draw(lists(text(min_size=1,
                           alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
                      min_size=header_len, max_size=header_len, unique=True))


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
    final_header_len = draw(integers(min_value=1, max_value=10))
    return _get_header_and_column_types(draw, final_header_len, final_header_len)


@overload
def _get_header_and_column_types(draw, header: isa(int), columns: isa(int)):
    if header == columns:

        header_fields = draw_header(draw, header)

        return header_fields, len(header_fields)
    else:
        raise InvalidArgument("Header and columns must be of the same size")


@overload
def _get_header_and_column_types(draw, header: is_none, columns: isa(int)):
    return _get_header_and_column_types(draw, columns, columns)


@overload
def _get_header_and_column_types(draw, header: isa(int), columns: is_none):
    return _get_header_and_column_types(draw, header, header)


@overload
def _get_header_and_column_types(draw, header: is_none, columns: is_seq):
    return draw_header(draw, len(columns)), columns


@composite
def csv(draw, header=None, columns=None,lines=None):
    """
    Strategy to produce a CSV string. Uses `data_rows` strategy to generate the values. Refer to the `data_rows`
    strategy for more details about the `columns` and `lines` parameter.
    
    :param draw:
    :param header: if a list of strings, these will be used as the header for each column, according to their position.
    If an int, this parameter will define the number of columns to be used. If not provided, the number of columns will
    be drawn randomly or the `columns` param will be used.
    :param columns: If a list of strategies, these will be used to draw the values for each column.
    If an int, this parameter will define the number of columns to be used. If not provided the number of columns will
    be drawn randomly or the `header` param will be used.
    :param lines: number of rows in the CSV.
    :return: a string in CSV format
    """
    header, columns = _get_header_and_column_types(draw, header, columns)

    rows = draw(data_rows(lines=lines, columns=columns))
    data = [dict(zip(header, d)) for d in rows]
    return records2csv(data).getvalue()
