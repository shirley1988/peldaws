from flask import jsonify
import praat
from praat import app

@app.route('/spectrum/get-bounds/<sound>')
def spectrumFrequencyBounds(sound):
    # Script file
    script = praat._scripts_dir + "spectrumFreqBounds";

    # Run script and get output
    output = praat.runScript(script, [sound, praat._sounds_dir])

    # Split output into an array
    res = output.split()

    # Create JSON object to return
    bounds = {
       "low": float(res[0]),
       "high": float(res[2])
    }

    return jsonify(bounds)

