from flask import jsonify
import praat
from praat import app

@app.route('/intensity/get-bounds/<sound>')
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
    
@app.route('/intensity/get-mean/<sound>/<start>/<end>')
def intensityMean(sound, start, end):
    script = praat._scripts_dir + "intensityMean";
    return praat.runScript(script, [sound, start, end, praat._sounds_dir])
