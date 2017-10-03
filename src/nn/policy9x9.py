"""Stuff to define, train, save and use the policy net

The data structures are all based on how the OpenAI gym defines it's Go9x9-v0
environment.
"""
from datetime import datetime
from os import path

import keras
import numpy as np
from keras import models, layers, backend as K


BOARD_SIZE = 9
BOARD_ACTIONS = list(range(9*9))
PASS_ACTION = 81
RESIGN_ACTION = 82
ACTION_SPACE = BOARD_ACTIONS + [PASS_ACTION] + [RESIGN_ACTION]
BOARD_SHAPE = (3,9,9)
BOARD_SHAPE_1 = (1,3,9,9)


def rewardloss(actionreward, policy):
    """Calculate expected loss

    Given a reward for each action and the current policy, calculate the expected return.
    Losses are minimized, so the sign of reward must be inverted so a positive reward is
    negative loss.

    This is a custom keras loss function which has the

    :param actionreward: tensor with dim n x (action space)
    :param policy: tensor with dim n x (action space)
    :return: scalar tensor
    """
    return -K.dot(actionreward, K.transpose(policy))


class PolicyNet:
    """The policy network model

        Defines the neural net architecture for the policy net, ie the neural net which
        calculates the action sampling distribution.
    """
    def __init__(self):
        self._build()

    def _build(self, summary=True, **kwargs):
        """Creates neurak network architecture

        :param summary: boolean         True -> prints keras model summary
        :param kwargs: unpacked dict    model.compile keywords
        :return: keras Model
        """
        inputs = layers.Input(shape=BOARD_SHAPE)
        zeros = layers.ZeroPadding2D((1,1))(inputs)
        conv = layers.Convolution2D(filters=16, kernel_size=(3, 3), activation='elu')(zeros)
        flat = layers.Flatten()(conv)
        hidden = layers.Dense(2 ** 8, activation='elu')(flat)
        bn = layers.BatchNormalization()(hidden)
        output = layers.Dense(len(ACTION_SPACE), activation='softmax')(bn)
        model = models.Model(inputs=inputs, outputs=output)

        model.compile(optimizer=kwargs.pop('optimizer', 'adam'),
                           loss=kwargs.pop('loss', rewardloss),
                           **kwargs
                           )
        if summary:
            print(model.summary())

        self.model = model

    def train(self, observations, actionrewards, **kwargs):
        """Train model on observations given the action's rewards

        :param observations: array
        :param actionrewards: array
        :param kwargs: unpacked dict    model.fit keywords
        """
        self.model.fit(observations,
                       actionrewards,
                       verbose=kwargs.pop('verbose', 2),
                       **kwargs
                       )

    def probailities(self, position, **kwargs):
        """Action policy for given 9x9 position

        :param position: array          OpenAI Go9x9-v0 board position
        :param kwargs: unpacked dict    model.predict keywords
        :return: array                  action probabilities
        """
        if position.shape == BOARD_SHAPE:
            position = position.reshape(BOARD_SHAPE_1)

        return np.array(self.model.predict(position, **kwargs)).reshape((len(ACTION_SPACE),))

    def move(self, position):
        """Make a move from 9x9 go board

        :return: int    move from 9x9 game
        """
        return np.random.choice(ACTION_SPACE, p=self.probailities(position=position))

    def save(self, fileheader, folder='models'):
        """Save the model json and weights

        Files are saved with a time tag to ensure uniqueness.

        :param fileheader: str    prepended to both file names
        :param folder: str        folder to save model and weights
        """
        time = datetime.datetime.now().strftime('%Y%m%d%H%M')
        filename = '_'.join([fileheader, time])

        h5name = '.'.join([filename, 'h5'])
        self.model.save(path.join(folder, h5name))

    def load_model(self, h5model):
        """Load model from json description

        This will replace self.model

        :param h5model:
        """
        self.model = models.load_model(h5model)


if __name__ == '__main__':
    from quilt.data.andrewbrown import gofamiliar as gf

    import sys

    print(sys.path)

    observations = np.load(gf.positions())
    actionrewards = keras.utils.to_categorical(np.load(gf.moves())) * np.load(gf.rewards()).reshape(10430,1)
    net = PolicyNet()
    net.train(observations=observations, actionrewards=actionrewards, epochs=1)

    net.save('policy0,0')

