import os
import sys
sys.path.append("./model")

from werkzeug.exceptions import HTTPException as WerkzeugException
from error import HTTPException
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from model import build_model
model_ = build_model()

from sass import compile
compile(dirname=("static/sass","static/css"))

app = Flask(__name__, static_url_path="/static")
app.debug = False
CORS(app)


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, (HTTPException, WerkzeugException)): 
        return jsonify(error=e.code, description=e.description, **getattr(e, "detail", dict())), e.code
    
    if not app.debug:
        return jsonify(error=500, description="An unexpected error occurred"), 500
        
    trace = []
    tb = e.__traceback__
    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next
    return jsonify(error=500, type=type(e).__name__, description=str(e), trace=trace), 500

@app.route("/api/price/", methods=["POST"])
def predict():
    params = request.json
    alpha = params.pop("alpha", 0.15)
    return jsonify(model_.predict(params, alpha=alpha))

@app.route('/')
def landing():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(threaded=True, port=5000)
