#!/usr/bin/python
#Flask rest endpoint for segmentation
from flask import Flask, request
import json
app = Flask(__name__)

#dummy segment endpoint
@app.route("/segment")
def segment():
  x = int(request.args.get("x", "0"))
  y = int(request.args.get("y", "0"))
  z = int(request.args.get("z", "0"))
  stack = request.args.get("stack", "")
  threshold = float(request.args.get("threshold", "0.5"))
  return json.dumps([[x, y-7], [x+3, y-3], [x+4, y], [x+3, y+7], [x, y+7], [x-3, y+3], [x-4, y], [x-3, y-7]])

if __name__ == "__main__":
  app.run()