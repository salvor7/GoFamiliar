import itertools
from numpy import infty
from pytest import fixture

from util.unionfind import UnionFind

TESTING_PRIME = 13

@fixture(params=[1, 10, 100, 1000, 10000, 100000, infty])
def fixture_uf(request):
    return UnionFind(size_limit=request.param)

def test_uf_init(fixture_uf):
    assert (len(fixture_uf._pointers) == fixture_uf.size_limit) or (len(fixture_uf) == 0)
    assert len(fixture_uf) == len(fixture_uf._pointers)
    for pt in fixture_uf:
        assert fixture_uf._pointers[pt] == pt

@fixture()
def fixture_unions(fixture_uf):
    if (fixture_uf.size_limit is infty):
        _ = fixture_uf[2 ** TESTING_PRIME - 1]

    for pt in fixture_uf:
        fixture_uf[pt] = (pt % TESTING_PRIME)
    return fixture_uf

def test_union_find(fixture_unions):
    unique_pointers = min(fixture_unions.size_limit, TESTING_PRIME)
    assert unique_pointers == len(set(fixture_unions._pointers))

    for pt in fixture_unions:
        assert fixture_unions[pt] == (pt % TESTING_PRIME)

    if fixture_unions.size_limit is infty:
        assert len(fixture_unions) == 2 ** TESTING_PRIME
        for pt in range(len(fixture_unions), 2 ** (TESTING_PRIME+1)):
            fixture_unions[pt] = pt % TESTING_PRIME
        assert len(fixture_unions) == 2 ** (TESTING_PRIME+1)

    for i in range(unique_pointers):
        fixture_unions[i] = 0
        for idx, pt in enumerate(fixture_unions):
            assert idx == pt        #test that the pointer starts, not the pointer ends are returned
            if pt % TESTING_PRIME <= i:
                assert fixture_unions[pt] == 0
                assert fixture_unions._pointers[pt] == 0  #test pointer update
            else:
                assert fixture_unions[pt] == pt % TESTING_PRIME
                assert fixture_unions._pointers[pt] == pt % TESTING_PRIME

    assert len(set(fixture_unions._pointers)) == 1

def test_uf_exceptions(fixture_unions):
    def key_find(key):
        _ = fixture_unions[key]
    def assign_key(key):
        fixture_unions[0] = key
    def assign_to_key(key):
        fixture_unions[key] = 0

    bad_keys = [-8.1, 7.4, 'l']
    if fixture_unions.size_limit is not infty:
        too_large_keys = [fixture_unions.size_limit*2, -fixture_unions.size_limit*2]
    else:
        too_large_keys = []

    for key, statement in itertools.product(bad_keys + too_large_keys,
                                            [key_find, assign_key, assign_to_key]):
        try:
            statement(key)
        except TypeError:
            assert key in bad_keys
        except IndexError:
            assert abs(key) >= fixture_unions.size_limit
        else:
            assert key == 0

    try:
        del fixture_unions[0]
    except AttributeError:
        pass
    else:
        assert False
