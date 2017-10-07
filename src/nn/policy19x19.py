"""Stuff to define, train, save and use the policy net

The data structures are all based on how the OpenAI gym defines it's Go9x9-v0
environment.
"""
from datetime import datetime
from os import path

import keras
import numpy as np
from keras import models, layers, backend as K
from keras.preprocessing import image


BOARD_SIZE = 19
ACTION_SPACE = list(range(BOARD_SIZE**2))
BOARD_SHAPE = (19,19)
BOARD_SHAPE_1 = (1,19,19)


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
        activation = 'selu'

        stones = layers.Input(shape=BOARD_SHAPE)
        open = layers.Input(shape=BOARD_SHAPE)
        open_flat = layers.Flatten()(open)

        zeros1 = layers.ZeroPadding2D((1,1))(stones)
        conv1 = layers.Convolution2D(filters=32, kernel_size=(3, 3), activation=activation)(zeros1)

        zeros2 = layers.ZeroPadding2D((1,1))(conv1)
        conv2 = layers.Convolution2D(filters=32, kernel_size=(3, 3), activation=activation)(zeros2)

        flat = layers.Flatten()(conv2)

        hidden1 = layers.Dense(2 ** 10, activation=activation)(flat)
        bn1 = layers.BatchNormalization()(hidden1)

        hidden2 = layers.Dense(2 ** 10, activation=activation)(bn1)
        bn2 = layers.BatchNormalization()(hidden2)

        soft = layers.Dense(len(ACTION_SPACE), activation='sigmoid')(bn2)

        output = layers.Multiply()([soft, open_flat])

        model = models.Model(inputs=[stones, open], outputs=output)

        model.compile(optimizer=kwargs.pop('optimizer', keras.optimizers.Adagrad()),
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
        self.model.fit([observations[:,:2,:,:], observations[:,2,:,:]],
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

        return np.array(self.model.predict([position[:, :2, :, :], position[:,2,:,:]], **kwargs)).reshape((len(ACTION_SPACE),))

    def move(self, position):
        """Make a move from 9x9 go board

        :return: int    move from 9x9 game
        """
        probs = self.probailities(position=position)
        probs = probs / np.sum(probs)
        return np.random.choice(ACTION_SPACE, p=probs)

    def save(self, fileheader, folder='models'):
        """Save the model json and weights

        Files are saved with a time tag to ensure uniqueness.

        :param fileheader: str    prepended to both file names
        :param folder: str        folder to save model and weights
        """
        time = datetime.now().strftime('%Y%m%d%H%M')
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
    actionrewards = keras.utils.to_categorical(np.load(gf.moves()) % 81, num_classes=81) * np.load(gf.rewards()).reshape(10430,1)
    net = PolicyNet()
    net.train(observations=observations, actionrewards=actionrewards, epochs=1)

    net.save('policy')

