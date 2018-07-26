import string

from hypothesis.strategies import text, lists
from meza.convert import records2csv

from hypothesis_csv._data_rows import *
from hypothesis_csv.type_utils import *


def draw_header(draw, header_len):
    return draw(lists(text(min_size=1,
                           alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
                      min_size=header_len, max_size=header_len, unique=True))



@overload
def get_header_and_column_types(draw, header, columns):
    raise InvalidArgument("Header or column are of invalid type")


@overload
def get_header_and_column_types(draw, header: is_seq,
                                columns: is_none):
    return header, len(header)


@overload
def get_header_and_column_types(draw, header: is_none, columns: is_none):
    final_header_len = draw(integers(min_value=1, max_value=10))
    return get_header_and_column_types(draw, final_header_len, final_header_len)


@overload
def get_header_and_column_types(draw, header: isa(int), columns: isa(int)):
    if header == columns:

        header_fields = draw_header(draw, header)

        return header_fields, len(header_fields)
    else:
        raise InvalidArgument("Header and columns must be of the same size")


@overload
def get_header_and_column_types(draw, header: is_none, columns: isa(int)):
    return get_header_and_column_types(draw, columns, columns)


@overload
def get_header_and_column_types(draw, header: isa(int), columns: is_none):
    return get_header_and_column_types(draw, header, header)


@overload
def get_header_and_column_types(draw, header: is_none, columns: is_seq):
    return draw_header(draw, len(columns)), columns


@composite
def csv(draw, header=None, lines=None, columns=None):
    header, columns = get_header_and_column_types(draw, header, columns)

    rows = draw(data_rows(lines=lines, columns=columns))
    data = [dict(zip(header, d)) for d in rows]
    return records2csv(data).getvalue()