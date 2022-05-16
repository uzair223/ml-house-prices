from typing import Callable
from numpy import ndarray

MatrixFunction = Callable[[ndarray], ndarray]
LossFunction = Callable[[ndarray, ndarray], ndarray]
WeightsInitFunction = Callable[[int,int],ndarray]

class BaseOptimiser(object):
    def __init__(self):
        # self.reset()
        pass

    def reset(self):
        raise NotImplementedError()
    
    def update(self, grad:ndarray, id:str) -> ndarray:
        raise NotImplementedError()

class BaseLayer(object):
    def __init__(self, id:str=None):
        self.id = id
        # self.reset()
    
    def reset(self):
        self.inp = None

    def forward(self, inp:ndarray) -> ndarray:
        raise NotImplementedError()

    def backward(self, grad:ndarray, optimiser:BaseOptimiser) -> ndarray:
        raise NotImplementedError()

class ActivationLayer(BaseLayer):
    def __init__(self, fn:MatrixFunction, prime:MatrixFunction, id:str=None):
        super().__init__(id)
        self.fn = fn
        self.prime = prime
    
    def forward(self, inp):
        self.inp = inp # storing x for back propagation
        return self.fn(inp)

    def backward(self, grad, optimiser): # optimiser parameter for consistency, will not be used
        return self.prime(self.inp) * grad # hadamard product - applying chain rule