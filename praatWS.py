from flask import Flask, jsonify, request, send_from_directory
from flask.ext.cors import CORS
import praat
import os

app = Flask(__name__)
CORS(app)

_images_dir = "images/"
_scripts_dir = "scripts/"
_sounds_dir = "sounds/"

@app.route('/')
def index():
    return "REST API to run scripts on Praat"

@app.route('/drawSound/<sound>/<startTime>/<endTime>/<showPitch>/<showIntensity>/<showFormants>')
def drawSound(sound, startTime, endTime, showPitch, showIntensity, showFormants):
    script = _scripts_dir + "drawSpectrogram";

    #Parameters to the script
    params = [sound, startTime, endTime, showPitch, showIntensity, showFormants, _sounds_dir, _images_dir]
    
    #Image name will be a combination of relevant params joined by a period.
    image = _images_dir + ".".join(params[:-2]) + ".png"

    #Add image name to params list
    params.append(image)

    #If image does not exist, run script
    if not os.path.isfile(image):
       praat.runScript(script, params);
    
    resp = app.make_response(open(image).read())
    resp.content_type = "image/jpeg"
    return resp

@app.route('/getBounds/<sound>')
def getBounds(sound):
    script = _scripts_dir + "getBounds";
    output = praat.runScript(script, [sound, _sounds_dir])
    res = output.split()
    bounds = {
        "start": float(res[0]),
        "end": float(res[2])
    };
    return jsonify(bounds);

@app.route('/play/<sound>')
def playSound(sound):
    fullpath = _sounds_dir + sound
    resp = app.make_response(open(fullpath).read())
    resp.content_type = "audio/wav"
    return resp

@app.route('/getEnergy/<sound>')
def getEnergy(sound):
    script = _scripts_dir + "getEnergy";
    return praat.runScript(script, [sound, _sounds_dir])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
