import numpy as np
class ConformalRegression(object):
    def __init__(self, model):
        self.model = model

    def calibrate(self, cal_X, cal_y):
        yhat = self.model.predict(cal_X)
        self.resid_ = np.abs(cal_y-yhat)
        return self

    def fit(self, X, y, cal_X, cal_y, **kwargs):
        self.model.fit(X, y, **kwargs)
        return self.calibrate(cal_X,cal_y)

    def predict(self, X, alpha = None):
        yhat = self.model.predict(X)

        if alpha is None:
            return yhat
        if alpha >= 1 or alpha <= 0:
            raise ValueError("'alpha' must be in interval (0, 1) or None")

        quantile = np.quantile(self.resid_, 1 - alpha)
        yhat_low = yhat - quantile
        yhat_up = yhat + quantile
        
        return yhat, np.column_stack([yhat_low, yhat_up])
