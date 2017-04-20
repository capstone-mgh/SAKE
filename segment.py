#!/usr/bin/python
#Flask rest endpoint for segmentation
from flask import Flask, request
import json
import numpy as np
from sake import Sake
app = Flask(__name__)

@app.route("/version")
def index():
    return "0.17"

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
    windowWidth = int(request.args.get("windowWidth", 400))
    #window center
    windowCenter = int(request.args.get("windowCenter", 40))
    #series id
    seriesInstanceUid = request.args.get("seriesInstanceUid", "")
    #instance id
    sopInstanceUid = request.args.get("sopInstanceUid", "")

    sake = Sake("/opt/bitnami/apache2/htdocs/" + patientName)
    #mask, mask_offset, polygon = sake.segmentImage(z, x, y)
    #TODO fix this coordinates hack
    mask, mask_offset, polygon = sake.segmentImage(z, y, x)
    mask = mask.T
    mask_offset = np.array([mask_offset[1], mask_offset[0]])
    polygon = np.column_stack((polygon[:,1], polygon[:,0]))
    data = {
            "mask": mask.tolist(),
            "maskOffset": mask_offset.tolist(),
            "polygon": polygon.tolist()
    }
    #frontend expects a json object with polygon and optionally mask + maskOffset
    #returning a blank object or object with empty polygon will stop z-propagation
    return json.dumps(data)

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == "__main__":
    app.run()