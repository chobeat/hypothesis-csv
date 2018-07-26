from multimethod import isa
import collections

# utils to support multimethod dispatching

def is_none(x):
    return x is None


def is_seq(x):
    return isa(collections.Iterable)(x) and not isa(str)(x)