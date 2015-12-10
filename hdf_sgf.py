import h5py
from os import path
import numpy as np

file = 'pro_collection.hdf5'
fpath = 'sgf_store'

pro_games = h5py.File(path.join(fpath, file), 'r')

#access moves
# m = 0
# for idx, key in enumerate(pro_games):
#     m += len(pro_games[key]['moves'])
# print(m)

print(len(pro_games['19']))
#access size 19 games
count_board = np.zeros(shape=(19,19), dtype=np.int)
for idx, game in enumerate(pro_games['19']):

    player, x, y = pro_games['19'][game][0]
    count_board[x-1, y-1] += 1

print(count_board)