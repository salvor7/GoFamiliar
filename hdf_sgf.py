import h5py
from os import path

file = 'sgfhdf5_doctest.hdf5'
fpath = 'sgf_store'

pro_games = h5py.File(path.join(fpath, file), 'r')

for key in pro_games:
    game = pro_games[key]
    attrs = game.attrs
    print(game, len(attrs))
