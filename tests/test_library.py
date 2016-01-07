from sgf.library import Library, doctest_dir, doctest_file


def test_sgf_position():
    position = Library(doctest_dir, doctest_file).sgf_position('chap075.sgf')
    assert position.komi == 5.5
    assert position.size == 19
    assert len(position.groups) == 46
    for group in position.groups:
        print(position[group])
