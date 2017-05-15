import sys

#Expand Python classes path with your app's path
sys.path.insert(0, "/opt/bitnami/apps/flask/sake")

from segment import app
application = app
