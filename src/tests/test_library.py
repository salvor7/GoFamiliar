import sgf


def test_sgf_position():
    position = sgf.Library(file=sgf.TEST_H5, direc=sgf.TEST_DIR, sgf_direc=sgf.TEST_DIR).sgf_position('chap075')
    assert position.komi == 5.5
    assert position.size == 19
