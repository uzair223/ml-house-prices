import numpy as np
from numpy import ndarray

from sklearn.base import BaseEstimator
from .base import BaseLayer, BaseOptimiser, LossFunction

import warnings

def mse(y, yhat):
    return np.mean(np.power(y-yhat, 2))

def mse_prime(y, yhat):
    return 2*(yhat-y)/y.size

class NeuralNetwork(BaseEstimator):
    def __init__(self, layers:"list[BaseLayer]", optimiser:BaseOptimiser, loss_fn:LossFunction=mse, loss_prime:LossFunction=mse_prime):
        self.layers = layers
        self.loss_fn = loss_fn
        self.loss_prime = loss_prime
        self.optimiser = optimiser

    def predict(self,X:ndarray) -> ndarray:
        out = np.asarray(X)
        # forward propagation
        for l in self.layers:
            out = l.forward(out)
        return out
