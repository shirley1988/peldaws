import subprocess
from flask import Flask
from flask.ext.cors import CORS

# Locations of required files
_images_dir = "images/"
_scripts_dir = "scripts/"
_sounds_dir = "sounds/"

# Run script 'scriptName' with the provided parameters
def runScript(scriptName, args):
   praatExec = ["praat/praat", "--run", "--no-pref-files", scriptName];
   praatExec.extend(args)
   output = subprocess.check_output(praatExec);

   return output

# Create flask app
app = Flask(__name__, static_url_path="")

# Add CORS headers to allow cross-origin requests
CORS(app)

#Import views
from views import * 
