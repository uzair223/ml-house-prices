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
ENCODING = json.load(open(ENCODING_PATH, "r"))
PREPROCESS = json.load(open(SCALING_PATH, "r"))


def xtransform(inp):
    inp_ = inp.copy()
    for k, v in inp_.items():
        feat = PREPROCESS.get(k, {"mean": 0., "std": 1.})
        # rescaling features to normalised values
        inp_[k] = (v - feat["mean"]) / feat["std"]
    return array([list(inp_.values())])


OUTPUT = PREPROCESS.pop("price")


def ytransform(inp):
    # reversing normalisation
    return inp * OUTPUT["std"] + OUTPUT["mean"]


def build_model():
    conf = ConformalRegression(joblib.load(MODEL_PATH))
    conf.resid_ = joblib.load(RESID_PATH)
    return Predictor(conf, FEATURES, ENCODING, xtransform, ytransform)
