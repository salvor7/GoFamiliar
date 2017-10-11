from os import path

import sgf


def test_sgf_position():
    position = sgf.Library(file=path.join(sgf.TEST_DIR, 'libtests_sgf.h5'),
                           direc=sgf.TEST_DIR,
                           sgf_direc=sgf.TEST_DIR
                           ).sgf_position('chap075')
    assert position.komi == 5.5
    assert position.size == 19
