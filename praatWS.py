from flask import Flask, jsonify, request, send_from_directory
import praat

app = Flask(__name__, static_folder="../images")

_images_dir = "images/"
_scripts_dir = "scripts/"
_sounds_dir = "../sounds/"

@app.route('/')
def index():
    return "REST API to run scripts on Praat"

@app.route('/drawSound/<sound>/<startTime>/<endTime>/<showPitch>/<showIntensity>/<showFormants>')
def drawSound(sound, startTime, endTime, showPitch, showIntensity, showFormants):
    script = _scripts_dir + "drawSpectrogram";
    praat.runScript(script, [sound, startTime, endTime, showPitch, showIntensity, showFormants, _sounds_dir, _images_dir]);
    
    fullpath = _images_dir + sound + ".png"
    resp = app.make_response(open(fullpath).read())
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

@app.route('/queryEnergy/<sound>')
def queryEnergy(sound):
    return praat.runScript("queryEnergy", [sound, _sounds_dir])

if __name__ == '__main__':
    app.run(debug=True)
