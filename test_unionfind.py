from unionfind import UnionFind
import pytest

@pytest.fixture(params=[0, 1, 10, 100, 1000, 10000, 100000])
def unionfind(request):
    return UnionFind(size_limit=request.param)

def test_uf_init(unionfind):
    assert len(unionfind.pointers) == unionfind.size_limit
    assert len(unionfind) == len(unionfind.pointers)
    for pt in unionfind:
        assert unionfind.pointers[pt] == pt

