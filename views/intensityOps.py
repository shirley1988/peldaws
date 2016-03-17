from flask import jsonify
import praat
from praat import app

@app.route('/intensity/get-bounds/<sound>')
def intensityBounds(sound):
    # Patht to script
    script = praat._scripts_dir + "intensityBounds";

    # Run script
    output = praat.runScript(script, [sound, praat._sounds_dir])

    # Split output into an array
    res = output.split()

    # Create JSON object to return
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

@app.route('/intensity/value-at-time/<sound>/<time>')
def intensityValueAtTime(sound, time):
    script = praat._scripts_dir + "intensityValueAtTime";
    return praat.runScript(script, [sound, time, praat._sounds_dir])

