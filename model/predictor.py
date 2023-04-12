from werkzeug.exceptions import BadRequest


class Predictor(object):

    def __init__(self,
                 model,
                 features,
                 encoding=None,
                 xtransform=lambda x: x,
                 ytransform=lambda x: x):
        self.model = model
        self.features = features
        self.encoding = encoding
        self.xtransform = xtransform
        self.ytransform = ytransform

    def encode(self, inp):
        if self.encode is None:
            return inp
        inp_ = inp.copy()
        for feat, encode in self.encoding.items():
            try:
                inp_[feat] = encode[inp_[feat]]  # encoding category value
            except KeyError:
                # unknown category
                raise BadRequest(
                    f"Invalid value for feature '{feat}': {inp[feat]}")
        return inp_

    def predict(self, inp, alpha=None):
        # checking for missing or unknown features
        unknown = inp.keys() - self.features  # X intersection F
        missing = self.features - inp.keys()  # F intersection X
        if len(unknown) > 0:
            raise BadRequest(f"Unknown fields: {list(unknown)}")
        if len(missing) > 0:
            raise BadRequest(f"Missing fields: {list(missing)}")
        inp_ = self.encode({k: inp[k]
                            for k in self.features})  # encoding categories
        # converting datatypes to numerical
        for k, v in inp_.items():
            try:
                inp_[k] = float(v)
            except:
                raise BadRequest(f"Invalid datatype: {k}")
        inp_ = self.xtransform(inp_)  # normalising input
        # interval prediction
        if alpha is not None and alpha != 0:
            yhat, interval = [
                self.ytransform(y).reshape(-1)
                for y in self.model.predict(inp_, alpha)
            ]
            return {"low": interval[0], "point": yhat[0], "high": interval[1]}
        # point prediction
        yhat = self.ytransform(self.model.predict(inp_)[0,0])
        return {"point": yhat}
