#!/usr/bin/python
#Flask rest endpoint for segmentation
from flask import Flask, request
import json
from sake import Sake
app = Flask(__name__)

@app.route("/version")
def index():
        return "0.12"

@app.route("/segment")
def segment():
        #x-position
        x = int(request.args.get("x", "0"))
        #y-position
        y = int(request.args.get("y", "0"))
        #0-based z-index
        z = int(request.args.get("z", "0"))
        #url to image
        imageId = request.args.get("imageId", "")

        #todo clean up frontend api
        patientId = imageId.split("/")[3]
        path = "/opt/bitnami/apache2/htdocs/" + patientId
        print path

        sake = Sake(path)
        print "webparams", x, y, z
        polygon = sake.segmentImage(z, x, y)
        return json.dumps(polygon.tolist())

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == "__main__":
#       app.debug = True
        app.run()
