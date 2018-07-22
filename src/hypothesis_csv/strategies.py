from hypothesis.strategies import composite, integers, floats, text, one_of, sampled_from
from hypothesis import settings, seed
from hypothesis.errors import InvalidArgument
from meza.convert import records2csv
import string
import functools


def is_seq(x):
    is_seq = True
    try:
        iter(x)
    except:
        is_seq = False

    return is_seq


def get_columns(draw, columns_param):
    valid_column_types = [integers, floats,
                          functools.partial(text, min_size=1, max_size=10,
                                            alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits)]

    if is_seq(columns_param):
        columns = columns_param
    else:
        if not columns_param:
            num_columns = draw(integers(min_value=1, max_value=10))
        elif isinstance(columns_param, int):
            num_columns = columns_param
        else:
            raise InvalidArgument("columns parameter must either be an integer or a list of strategies")

        columns = [draw(sampled_from(valid_column_types))() for _ in range(num_columns)]

    return columns


def get_lines_num(draw, lines_param):
    if lines_param is None:
        return draw(integers(min_value=1, max_value=100))
    elif isinstance(lines_param, int):
        return lines_param
    else:
        raise InvalidArgument("lines param must be an integer")


@composite
def data_rows(draw, lines=None, columns=None):
    columns = get_columns(draw, columns)
    lines_num = get_lines_num(draw, lines)
    rows = [tuple(draw(column) for column in columns) for _ in range(lines_num)]

    return rows


@composite
def csv(draw, header=None, *args, **kwargs):
    if not header:
        final_header_len = draw(integers(min_value=1, max_value=10))
        header = []
        while (len(header) < final_header_len):
            new_column = draw(
                text(min_size=1, alphabet=string.ascii_lowercase + string.ascii_uppercase + string.digits))
            if new_column not in header:
                header.append(new_column)

    rows = draw(data_rows(columns=len(header), *args, **kwargs))
    data = [dict(zip(header, d)) for d in rows]
    return records2csv(data).getvalue()
