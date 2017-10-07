
import numpy as np


def convert_observation(go_obs):
    """Convert openai game observations into greyscale image

    BLACK is set to pixel value 1
    WHITE is set to pixel value 255
    BOARD is set to pixel value 127

    :param go_obs: np.array     SIZE x SIZE x 3
    :return: np.array           SIZE x SIZE
    """
    if len(go_obs.shape) == 3:
        go_obs = go_obs[np.newaxis]

    colour_values = np.array((1, 255, 127)).reshape(1,3,1,1)       # black, white, board
    scaled_obs = go_obs * colour_values
    return np.sum(scaled_obs, axis=1)
