import numpy as np
from .base import BaseOptimiser

class AdamOptimiser(BaseOptimiser):
    def __init__(self, lr:float=0.01, beta1:float=0.9, beta2:float=0.999, eps:float=1e-8):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.reset()

    def reset(self):
        self.cache_m = dict()
        self.cache_v = dict()
        self.cache_t = dict()

    def update(self, grad, id):
        # retrieve previous iteration variables
        m = self.cache_m.get(id, 0)
        v = self.cache_v.get(id, 0)
        t = self.cache_t.get(id, 1)
        # update variables for current iteration
        self.cache_m[id] = self.beta1 * m + (1 - self.beta1) * grad
        self.cache_v[id] = self.beta2 * v + (1 - self.beta2) * grad ** 2
        # bias-corrected variable
        m_corrected = self.cache_m[id] / (1 - self.beta1 ** t)
        v_corrected = self.cache_v[id] / (1 - self.beta2 ** t)
        self.cache_t[id] = t + 1
        # delta calculation
        delta = self.lr * m_corrected / (np.sqrt(v_corrected) + self.eps)
        return delta