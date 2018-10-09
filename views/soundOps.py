from flask import jsonify, request

from xml.etree import cElementTree as ET
#from lxml import etree
from shutil import copyfile

import os
import time

import praat
import utils
from praat import app

## added from ElanLocal.py
import subprocess
from flask import Flask
from flask_cors import CORS
from flask import send_from_directory
from flask import abort, send_file
from werkzeug import secure_filename
from shutil import copyfile
from pympi import Eaf
from pydub import AudioSegment
from pylab import *
import wave
import pympi
import datetime
import re
import sys
import pathlib
##



@app.route('/draw-sound/<sound>/<startTime>/<endTime>/')
def drawSound(sound, startTime, endTime):

    # Get URL parameters
    showSpectrogram = '0' if request.args.get("spectrogram") is None else '1'
    showPitch = '0' if request.args.get("pitch") is None else '1'
    showIntensity = '0' if request.args.get("intensity") is None else '1'
    showFormants = '0' if request.args.get("formants") is None else '1'
    showPulses = '0' if request.args.get("pulses") is None else '1'

    # Script file
    script = praat._scripts_dir + "drawSpectrogram";

    # Parameters to the script
    params = [sound, startTime, endTime,
             showSpectrogram, showPitch, showIntensity, showFormants, showPulses,
             praat._sounds_dir, praat._images_dir];

    # Image name will be a combination of relevant params joined by a period.
    image = praat._images_dir + ".".join(params[:-2]) + ".png"

    # Add image name to params list
    params.append(image)

    # If image does not exist, run script
    if not os.path.isfile(image):
       praat.runScript(script, params)
       utils.resizeImage(image)

    # Image should be available now, generated or cached
    resp = app.make_response(open(image).read())
    resp.content_type = "image/png"
    return resp

@app.route('/get-bounds/<sound>')
def getBounds(sound):
    script = praat._scripts_dir + "getBounds";
    output = praat.runScript(script, [sound, praat._sounds_dir])
    res = output.split() # Split output into an array

    # Get last modified time of the sound file
    # Should think about either changing the service name,
    # or obtaining last modified time using a different service
    lastModifiedTime = time.ctime(os.path.getctime(os.path.join(praat._sounds_dir, sound)))

    # Create JSON object to return
    bounds = {
        "start": float(res[0]),
        "end": float(res[2]),
        "min": float(res[4]),
        "max": float(res[6]),
        "lastModified": lastModifiedTime
    };
    return jsonify(bounds);

@app.route('/play/<sound>')
def playSound(sound):
    # Get the path to the sound file
    fullpath = praat._sounds_dir + sound

    ## added to test play functionality using praat script
    #script = praat._scripts_dir + "test"
    #params = [sound, praat._sounds_dir]
    #praat.runScript(script, params)

    # Open stream to file
    resp = app.make_response(open(fullpath).read())

    # Set file type like audio/mp3 or audio/wav
    resp.content_type = "audio/" + utils.fileType(sound)
    #print str(resp.content_type)
    #print str(resp)
    return resp

@app.route('/get-energy/<sound>')
def getEnergy(sound):
    script = praat._scripts_dir + "getEnergy";
    return praat.runScript(script, [sound, praat._sounds_dir])
