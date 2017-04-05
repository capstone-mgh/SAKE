# SAKE
Server side code

# Deploying a Flask app to the gcloud server
(adapted from http://csparpa.github.io/blog/2013/03/how-to-deploy-flask-applications-to-apache-webserver.html)

Change user to root (or sudo all the following commands)
````
sudo su
````
Change to app directory
````
cd /opt/bitnami/apps/flask
````

Create a folder for your app
````
mkdir foldername
````

Add your app (py and wsgi file, see test app for example)
````
#test.py
from flask import Flask, request
app = Flask(__name__)

@app.route('/hello')
def hello_world():
  name = request.args.get('name','')
  return 'Hello ' + name + '!'

if __name__ == '__main__':
  app.run()
````
````
#test.wsgi
import sys

#Expand Python classes path with your app's path
sys.path.insert(0, "/opt/bitnami/apps/flask/test")

from test import app
application = app
````

Edit the bottom of the httpd.conf configuration file to give access permission to your directory and point your url 
````
vim /opt/bitnami/apache2/conf/httpd.conf
````

````
<Directory /opt/bitnami/apps/flask/test>
  Require all granted
</Directory>
WSGIScriptAlias /flasktest /opt/bitnami/apps/flask/test/test.wsgi
````

Restart the Apache server
````
/opt/bitnami/ctlscript.sh restart apache
````
