from numpy import random
import numpy as np
import cProfile

#TODO turn into a ipy sheet and a unit test 

size = 19
number_games = 1000000

def random_game_accessor(number_games):
    yield_size = 2**14
    for __ in range(number_games//yield_size):
        yield random.random_integers(-1, 1, (yield_size, size, size))
    rem = number_games % yield_size
    yield random.random_integers(-1, 1, (rem, size, size))


def compute_spots(game_array_iter):
    black = np.zeros((size, size))
    white = np.zeros((size, size))

    corr_factor = 0.5/number_games
    for game_array in game_array_iter:
        bmw = np.sum(game_array, 0)
        bpw = np.sum(np.abs(game_array), 0)

        new_black = np.multiply(np.add(bmw, bpw), corr_factor)
        new_white = np.multiply(np.subtract(bmw, bpw), corr_factor)

        black = np.add(black, new_black)
        white = np.add(white, new_white)
    return black, white

def compute_score(black, white):
    return np.sum(np.add(black, white))

if __name__ == '__main__':
    all_games = random_game_accessor(number_games)
    cProfile.run('compute_spots(all_games)')