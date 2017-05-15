#!/usr/bin/python
#Flask rest endpoint for segmentation
from flask import Flask, request
from flask_cors import CORS
import json
import numpy as np
import h5py
from sake import Sake
from predict import Model

app = Flask(__name__)
model = Model()
annotations_dir = '/opt/bitnami/apps/flask/sake/annotations/'

CORS(app)

@app.route("/version")
def index():
    return "1.0"

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    print(request.args)
    if (request.data):
        print("request data length > 0")
        polygons = request.form["polygons"]
        x = int(request.form["x"])
        y = int(request.form["y"])
    else:
        polygons = np.zeros((2, 2, 2))
        x = 0
        y = 0
    print("POLYGON SIZE",polygons.shape)
    mal = float(model.get_malignancy(polygons))
    perc = float(model.get_percentiles(x, y, polygons))
    data = {"malignancy": mal, "percentile": perc}
    return json.dumps(data)

@app.route("/save", methods=["GET", "POST"])
def save():
    if (request.data):
        seriesId = request.form["seriesInstanceUid"]
        nodules = request.form["nodules"]
        f = h5py.File(annotations_dir+str(seriesId)+'.h5', 'w')
        data = f.create_dataset('series', data=nodules)
        return json.dumps(1)
    else:
        return json.dumps(0)

@app.route("/segment")
def segment():
    print "Request arguments"
    print request.args

    #x-position
    x = int(request.args.get("x", "0"))
    #y-position
    y = int(request.args.get("y", "0"))
    #0-based z-index
    z = int(request.args.get("z", "0"))
    #clicked x-position
    xOrig = int(request.args.get("xOrig", "0"))
    #clicked y-position
    yOrig = int(request.args.get("yOrig", "0"))
    #clicked z-index
    zOrig = int(request.args.get("zOrig", "0"))
    #patient name
    patientName = request.args.get("patientName", "")
    #window width
    windowWidth = float(request.args.get("windowWidth", 400))
    #window center
    windowCenter = float(request.args.get("windowCenter", 40))
    #series id
    seriesInstanceUid = request.args.get("seriesInstanceUid", "")
    #instance id
    sopInstanceUid = request.args.get("sopInstanceUid", "")

    sake = Sake("/opt/bitnami/apache2/htdocs/" + patientName)
    mask, mask_offset, polygon = sake.segmentImage(z, y, x)
    if polygon is not None:
        data = {
                "mask": mask.tolist(),
                "maskOffset": mask_offset.tolist(),
                "polygon": polygon.tolist()
        }
    else:
        data = {}
    #frontend expects a json object with polygon and optionally mask + maskOffset
    #returning a blank object or object with empty polygon will stop z-propagation
    return json.dumps(data)

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == "__main__":
    app.run()

