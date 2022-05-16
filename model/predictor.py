from error import BadRequest

class Predictor(object):
    def __init__(self, model, features, encoding=None, xtransform=lambda x: x, ytransform=lambda x: x):
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
                inp_[feat] = encode[inp_[feat]]
            except KeyError:
                raise BadRequest(description=f"Invalid value for '{feat}'", value=inp[feat])
        return inp_


    def predict(self, inp, alpha = None):
        unknown = inp.keys() - self.features
        missing = self.features - inp.keys()
	
        if len(unknown) > 0:
            raise BadRequest(description="Unknown fields", fields=list(unknown))
        if len(missing) > 0:
            raise BadRequest(description="Missing fields", fields=list(missing))
        
        inp_ = self.encode({k:inp[k] for k in self.features})
        for k, v in inp_.items():
            if not isinstance(v,(float,int)):
                try: inp_[k] = float(v)
                except: raise BadRequest("Invalid datatype", param=k)
        inp_ = self.xtransform(inp_)
	
        if alpha is not None:
            yhat, interval = [self.ytransform(y).reshape(-1) for y in self.model.predict(inp_, alpha)]
            return {
                "low": interval[0],
                "point": yhat[0],
                "high": interval[1]
            }
	
        yhat = self.ytransform(self.model.predict(inp_, alpha))
        return {
            "point": yhat
        }
