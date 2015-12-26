import numpy as np
import pytest
from util.unionfind import UnionFind

@pytest.fixture(params=[1, 10, 100, 1000, 10000, 100000, np.infty])
def unionfind(request):
    return UnionFind(size_limit=request.param)

def test_uf_init(unionfind):
    if (unionfind.size_limit is np.infty):
        unionfind[2**16]
    assert (len(unionfind._pointers) == unionfind.size_limit) or (unionfind.size_limit is np.infty)
    assert len(unionfind) == len(unionfind._pointers)
    for pt in unionfind:
        assert unionfind._pointers[pt] == pt

def test_uf_union(unionfind):
    assert False

def test_uf_find(unionfind):
    assert False

def test_uf_exceptions(unionfind):
    assert False
