from mysite.wsgi import application
import os
import firebase_admin
from firebase_admin import credentials

# App Engine by default looks for a main.py file at the root of the app
# directory with a WSGI-compatible object called app.
# This file imports the WSGI-compatible object of your Django app,
# application from mysite/wsgi.py and renames it app so it is discoverable by
# App Engine without additional configuration.
# Alternatively, you can add a custom entrypoint field in your app.yaml:
# entrypoint: gunicorn -b :$PORT mysite.wsgi
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.abspath("serviceAccountKey.json")
cred = credentials.Certificate(os.path.abspath("serviceAccountKey.json"))
default_app = firebase_admin.initialize_app(cred)
app = application
