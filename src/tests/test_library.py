from sgf.library import Library, doctest_dir, doctest_file


def test_sgf_position():
    position = Library(doctest_dir, doctest_file).sgf_position('chap075')
    assert position.komi == 5.5
    assert position.size == 19


def test_9by9_sgflibrary():
    _ = Library(direc='data\\test_sets',
                       file='test_sets.hdf5').sgf_position('tsumego013')