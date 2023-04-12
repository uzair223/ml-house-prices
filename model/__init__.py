import os, json
import sys

from . import algorithms
sys.modules["algorithms"] = algorithms

import joblib
from numpy import array

from .algorithms.conformal import ConformalRegression
from .predictor import Predictor

# emulating ordered set
FEATURES = dict.fromkeys(("year", "lat", "lng", "total_floor_area",
                          "number_habitable_rooms", "property_type")).keys()

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
MODEL_PATH = os.path.join(DATA_PATH, "model.bin")
ENCODING_PATH = os.path.join(DATA_PATH, "encoding.json")
SCALING_PATH = os.path.join(DATA_PATH, "scaling.json")
RESID_PATH = os.path.join(DATA_PATH, "conf_resid.bin")


def xtransform(scaling):
    def func(inp):
        inp_ = inp.copy()
        for k, v in inp_.items():
            feat = scaling.get(k, {"mean": 0., "std": 1.})
            # rescaling features to normalised values
            inp_[k] = (v - feat["mean"]) / feat["std"]
        return array([list(inp_.values())])
    return func


def ytransform(output_scale):
    def func(inp):
        # reversing normalisation
        return inp * output_scale["std"] + output_scale["mean"]
    return func

# loading encoding and scaling factors
def load_json_files():
    encoding = json.load(open(ENCODING_PATH, "r"))
    scaling = json.load(open(SCALING_PATH, "r"))
    output_scale = scaling.pop("price") # separating price scaling factors from features
    return encoding, scaling, output_scale

def build_model():
    encoding, scaling, output_scale = load_json_files()
    conf = ConformalRegression(joblib.load(MODEL_PATH))
    conf.resid_ = joblib.load(RESID_PATH)
    return Predictor(conf, FEATURES, encoding, xtransform(scaling), ytransform(output_scale))
