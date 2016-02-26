from flask import jsonify
import praat
from praat import app

@app.route('/spectrum/get-bounds/<sound>')
def spectrumFrequencyBounds(sound):
    script = praat._scripts_dir + "spectrumFreqBounds";
    output = praat.runScript(script, [sound, praat._sounds_dir])
    res = output.split()
    bounds = {
       "low": float(res[0]),
       "high": float(res[2])
    }

    return jsonify(bounds)

