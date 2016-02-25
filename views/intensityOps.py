from flask import jsonify
import praat
from praatWS import app

@app.route('/intensity/getBounds/<sound>')
def intensityBounds(sound):
    script = praat._scripts_dir + "intensityBounds";
    output = praat.runScript(script, [sound, praat._sounds_dir])
    res = output.split()
    bounds = {
       "min": float(res[0]),
       "max": float(res[2]),
       "mean": float(res[4])
    }

    return jsonify(bounds)

