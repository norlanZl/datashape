from __future__ import print_function, division, absolute_import

import numpy as np

from datashape.coretypes import *
from multipledispatch import dispatch
from time import strptime
from dateutil.parser import parse as dateparse
from datetime import datetime, date
from .py2help import _strtypes


__all__ = ['discover']


@dispatch(int)
def discover(i):
    return int64


@dispatch(float)
def discover(f):
    return float64


@dispatch(bool)
def discover(b):
    return bool_


@dispatch(complex)
def discover(z):
    return complex128


@dispatch(datetime)
def discover(dt):
    return datetime_


bools = {'False': False,
         'false': False,
         'True': True,
         'true': True}


string_coercions = [int, float, bools.__getitem__, dateparse]


@dispatch(_strtypes)
def discover(s):
    if not s:
        return None
    for f in string_coercions:
        try:
            return discover(f(s))
        except:
            pass

    return string


@dispatch((tuple, list))
def discover(seq):
    types = list(map(discover, seq))
    typ = unite(types)
    if not typ:
        return Tuple(types)
    else:
        return len(types) * typ


def unite(dshapes):
    """ Unite possibly disparate datashapes to common denominator

    >>> unite([10 * (2 * int32), 20 * (2 * int32)])
    dshape("var * 2 * int32")

    >>> unite([int32, int32, None, int32])
    option[int32]
    """
    if len(set(dshapes)) == 1:
        return dshapes[0]
    if all(isdimension(ds[0]) for ds in dshapes):
        dims = [ds[0] for ds in dshapes]
        if len(set(dims)) == 1:
            return dims[0] * unite([ds.subshape[0] for ds in dshapes])
        else:
            return var * unite([ds.subshape[0] for ds in dshapes])
    if any(ds is None for ds in dshapes):
        return Option(unite(filter(None, dshapes)))


@dispatch(dict)
def discover(d):
    return Record([[k, discover(d[k])] for k in sorted(d)])


@dispatch(np.number)
def discover(n):
    return from_numpy((), type(n))


@dispatch(np.ndarray)
def discover(X):
    return from_numpy(X.shape, X.dtype)
