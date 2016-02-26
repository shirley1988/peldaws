import subprocess
from flask import Flask
from flask.ext.cors import CORS

_images_dir = "images/"
_scripts_dir = "scripts/"
_sounds_dir = "sounds/"

def runScript(scriptName, args):
   praatExec = ["praat/praat", "--run", "--no-pref-files", scriptName];
   praatExec.extend(args)
   output = subprocess.check_output(praatExec);

   return output

app = Flask(__name__, static_url_path="")
CORS(app)

#Import views
from views import * 
