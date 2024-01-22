from collections.abc import Iterable

from multimethod import isa

# utils to support multimethod dispatching

def is_none(x):
    return x is None


def is_seq(x):
    return isa(Iterable)(x) and not isa(str)(x)
