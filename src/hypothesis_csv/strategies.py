import collections
import functools
import string

from hypothesis.errors import InvalidArgument
from hypothesis.strategies import composite, integers, floats, text, sampled_from, lists
from meza.convert import records2csv
from multimethod import overload, isa

valid_column_types = [integers, floats,
                      functools.partial(text, min_size=1, max_size=10,
                                        alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits)]


def is_none(x):
    return x is None


def is_seq(x):
    return isa(collections.Iterable)(x) and not isa(str)(x)


@overload
def get_columns(draw, columns):
    raise InvalidArgument("Columns parameter must either be an integer or a list of strategies")


@overload
def get_columns(draw, columns: isa(collections.Iterable)):
    return columns


@overload
def get_columns(draw, columns: isa(int)):
    columns = [draw(sampled_from(valid_column_types))() for _ in range(columns)]
    return columns


@overload
def get_columns(draw, columns: is_none):
    return get_columns(draw, draw(integers(min_value=1, max_value=10)))


@overload
def get_lines_num(draw, lines_param):
    raise InvalidArgument("Lines param must be an integer or None")


@overload
def get_lines_num(draw, lines_param: is_none):
    return draw(integers(min_value=1, max_value=100))


@overload
def get_lines_num(draw, lines_param: isa(int)):
    return lines_param


@composite
def data_rows(draw, lines=None, columns=None):
    lines_num = get_lines_num(draw, lines)
    columns = get_columns(draw, columns)
    rows = [tuple(draw(column) for column in columns) for _ in range(lines_num)]
    return rows


@overload
def get_header_and_column_types(draw, header, columns):
    raise InvalidArgument("Header or column are of invalid type")


@overload
def get_header_and_column_types(draw, header: lambda x: is_seq,
                                columns: is_none):
    return header, len(header)


@overload
def get_header_and_column_types(draw, header: is_none, columns: is_none):
    final_header_len = draw(integers(min_value=1, max_value=10))
    return get_header_and_column_types(draw, final_header_len, final_header_len)


@overload
def get_header_and_column_types(draw, header: isa(int), columns: isa(int)):
    final_header_len = header
    if header == columns:

        header_fields = draw(lists(text(min_size=1,
                                        alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits),
                                   min_size=final_header_len, max_size=final_header_len, unique=True))

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
    pass


@composite
def csv(draw, header=None, lines=None, columns=None):
    header, columns = get_header_and_column_types(draw, header, columns)

    rows = draw(data_rows(lines=lines, columns=columns))
    data = [dict(zip(header, d)) for d in rows]
    return records2csv(data).getvalue()
