from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__, static_url_path="")
CORS(app)

#Import views
from views import * 
