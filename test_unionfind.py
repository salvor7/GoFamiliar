from unionfind import UnionFind
import pytest

@pytest.fixture(params=[0, 1, 10, 100, 1000, 10000, 100000])
def unionfind(request):
    return UnionFind(size_limit=request.param)

