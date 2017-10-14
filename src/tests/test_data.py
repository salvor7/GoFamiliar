import h5py
import pytest

import sgf


@pytest.fixture(scope='module')
def pro_games():
    try:
        return h5py.File(sgf.SGF_H5, 'r')
    except OSError:
        sgf.create_pro_hdf5()
        return h5py.File(sgf.SGF_H5, 'r')


def test_all_pro_games_included(pro_games):
    """Assert all the games in the pro library are present"""
    assert len(pro_games) == 51508


def test_pro_games_dataleaves(pro_games):
    """Test the expected data leaves are for all games are present"""
    failes = []
    for game in pro_games:
        for dataleaf in ['moves', 'setup', 'gray']:
            try:
                pro_games[game][dataleaf]
            except KeyError:
                failes.append((game, dataleaf))

    assert not failes


def test_sgf_data_correct(pro_games):
    """ Test the data for a subsample of sgf

    Ensure all meta data is stored, and that the number of moves is correct
    """
    standard_attributes = ['FF', 'EV', 'PB', 'BR', 'PW', 'WR', 'KM', 'RE', 'DT', 'SZ']
    subsamplegames = {'HoshinoToshi-YamabeToshiro4762': (standard_attributes + ['PC', 'CA'], 411),
                      'HayashiYutaro-HashimotoUtaro4546': (standard_attributes + ['GM', 'CA'], 302),
                      '-1': (standard_attributes + ['PC', 'CA'], 284),
                      'ZouJunjie-ZhuSongli25339': (standard_attributes + ['RU', 'CA'], 161),
                      '.-.21425': (standard_attributes + ['PC', 'RU', 'CA'], 148),
                      'WangLei-WangYao35430': (standard_attributes + ['AP'], 121),
                      '-2432': (standard_attributes + ['PC', 'GM', 'CA'], 61),
                      }

    for gamename in subsamplegames:
        expected_attributes, expected_game_len = subsamplegames[gamename]

        # ensure all expected attributes are present
        for attr in expected_attributes:
            assert attr in pro_games[gamename].attrs

        moves = list(pro_games[gamename]['moves'])
        assert len(moves) == expected_game_len
        for m in moves:
            assert 0 <= m[0] < 19**2


def test_move_count_to_position_lengths(pro_games):
    """Comparing the number of moves to the number of positions

    In the pro sgf library, the number of moves recorded should be one less than the number of positions recorded as
    there is a new position after each move plus the first position, which isn't always a blank board.
    This test ensures that the counts are as expected.
    """
    for game in pro_games:
        assert len(pro_games[game]['moves']) + 1 == pro_games[game]['gray'].shape[0]
