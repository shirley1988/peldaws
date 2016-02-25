from flask import jsonify
import os

import praat
import utils
from praatWS import app

@app.route('/drawSound/<sound>/<startTime>/<endTime>/<showSpectrogram>/<showPitch>/<showIntensity>/<showFormants>/<showPulses>')
def drawSound(sound, startTime, endTime, showSpectrogram, showPitch, showIntensity, showFormants, showPulses):
    script = praat_scripts_dir + "drawSpectrogram";

    #Parameters to the script
    params = [sound, startTime, endTime,
              showSpectrogram, showPitch, showIntensity, showFormants, showPulses, 
              praat._sounds_dir, praat._images_dir];
    
    #Image name will be a combination of relevant params joined by a period.
    image = praat._images_dir + ".".join(params[:-2]) + ".png"

    #Add image name to params list
    params.append(image)

    #If image does not exist, run script
    if not os.path.isfile(image):
       praat.runScript(script, params)
       utils.resizeImage(image)

    resp = app.make_response(open(image).read())
    resp.content_type = "image/png"
    return resp

@app.route('/getBounds/<sound>')
def getBounds(sound):
    script = praat._scripts_dir + "getBounds";
    output = praat.runScript(script, [sound, praat._sounds_dir])
    res = output.split()
    bounds = {
        "start": float(res[0]),
        "end": float(res[2]),
        "min": float(res[4]),
        "max": float(res[6])
    };
    return jsonify(bounds);

@app.route('/play/<sound>')
def playSound(sound):
    fullpath = _sounds_dir + sound
    resp = app.make_response(open(fullpath).read())
    resp.content_type = "audio/" + utils.fileType(sound)
    return resp

@app.route('/getEnergy/<sound>')
def getEnergy(sound):
    script = praat._scripts_dir + "getEnergy";
    return praat.runScript(script, [sound, praat._sounds_dir])

