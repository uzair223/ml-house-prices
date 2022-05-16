from audioop import add
import numpy as np
from typing import Union
from .base import BaseLayer, ActivationLayer, WeightsInitFunction

class PerceptronLayer(BaseLayer):
    @staticmethod
    def xavier_init(n_in, n_out, seed=None):
        np.random.seed(seed)
        return np.random.normal(
            loc = 0.0,
            scale = np.sqrt(2/(n_in + n_out)),
            size = (n_in, n_out),
        )
        
    @staticmethod
    def he_init(n_in, n_out, seed=None):
        np.random.seed(seed)
        return np.random.normal(
            loc = 0.0,
            scale = np.sqrt(2/n_in),
            size = (n_in, n_out),
        )

    def __init__(self, n_in:int, n_out:int, weights_init:Union[str,WeightsInitFunction]="he", add_bias=True, id:str=None, seed=None):
        super().__init__(id)
        self.n_in = n_in
        self.n_out = n_out
        options = {
            "he":self.he_init,
            "kaiming":self.he_init,
            "xavier":self.xavier_init,
            "glorot":self.xavier_init,
        }
        self.seed = seed
        self.weights_init = options.get(weights_init,weights_init)
        if not callable(self.weights_init):
            raise ValueError(f"`weights_init` must be a string in {set(options.keys())} or callable(n_in, n_out, seed):ndarray[n_in, n_out]")
        self.add_bias = add_bias
        self.reset()
    
    def reset(self):
        super().reset()
        # initialise weights
        self.weights = self.weights_init(self.n_in, self.n_out, self.seed)
        self.bias = np.zeros((1,self.n_out)) # initialising bias - will remain zero if add_bias is False
        
    def forward(self, inp):
        self.inp = inp # storing input for back propagation
        return np.dot(self.inp, self.weights) + self.bias # y = w.x + b
        
    def backward(self, grad, optimiser):
        grad_inp = np.dot(grad, self.weights.T) # gradient of loss wrt input for backpropagation
        
        grad_weights = np.dot(self.inp.T, grad) # gradient of loss wrt weights
        grad_bias = np.mean(grad, axis=0) # gradient of loss wrt bias 

        self.weights -= optimiser.update(grad_weights, self.id+"weights")
        if self.add_bias:
            self.bias -= optimiser.update(grad_bias, self.id+"bias")
        return grad_inp


class LeakyReLU(ActivationLayer):
    def __init__(self, alpha:float, id:str=None):
        self.alpha = alpha
        super().__init__(self.fn, self.prime, id)

    def fn(self, inp):
        # x >= 0: x
        #  x < 0: x * alpha
        return np.maximum(inp, self.alpha*inp)

    def prime(self, inp):
        # x >= 0: 1
        #  x < 0: alpha
        return np.where(inp < 0, self.alpha, np.ones_like(inp))