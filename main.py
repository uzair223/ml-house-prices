import sys
from os import path
ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import json
from flask import Flask, request, redirect, url_for, jsonify, render_template
from werkzeug.exceptions import HTTPException

from model import build_model
import utils

app = Flask(__name__)
model_ = build_model()

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, (HTTPException)):
        error = e.description
    elif app.debug:
        error = str(e)
    else:
        error = "An unexpected error occured!"
    return redirect(url_for("render_landing", error=error))


@app.route("/api/predict")
def predict():
    args = request.args.to_dict()

    redirect_ = args.pop("redirect", "false").lower()
    alpha = args.pop("alpha", 0.45)
    postcode = args.pop("postcode")

    try:
        alpha = float(alpha)
    except ValueError:
        alpha = None

    # fetching data about postcode using findthatpostcode.uk api
    pcd_data = utils.findthatpostcode(postcode)
    args = dict(**args, **pcd_data["location"])
    yhat = model_.predict(args, alpha)
    if redirect_ == "true":  # redirecting to results page if specified
        return redirect(url_for("render_result", **dict(**yhat, pcd_data=pcd_data)))
    return jsonify(yhat)  # otherwise sending json response


@app.route("/")
def render_landing():
    return render_template("index.jinja", error=request.args.get("error"))


@app.route("/r")
def render_result():
        if (set(request.args.keys()) != {"high","point","low","pcd_data"}):
            return redirect(url_for("render_landing"))
        pcd_data = json.loads(request.args.get("pcd_data").replace("'",'"'))
        high = float(request.args.get("high"))
        point = float(request.args.get("point"))
        low = float(request.args.get("low"))
        return render_template("index.jinja",
                                pcd_data=pcd_data,
                                high=utils.formatNumber(high, 3),
                                point=f'{int(float(f"{point:.4g}")):,}',
                                low=utils.formatNumber(low, 3),
                                modal=True)