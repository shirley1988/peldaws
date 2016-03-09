import praat
from praat import app

@app.route('/harmonicity/get-min/<sound>/<start>/<end>')
def harmonicityGetMin(sound, start, end):
    script = praat._scripts_dir + "harmonicityGetMin";
    return praat.runScript(script, [sound, start, end, praat._sounds_dir])

@app.route('/harmonicity/get-max/<sound>/<start>/<end>')
def harmonicityGetMax(sound, start, end):
    script = praat._scripts_dir + "harmonicityGetMax";
    return praat.runScript(script, [sound, start, end, praat._sounds_dir])

@app.route('/harmonicity/value-at-time/<sound>/<time>')
def harmonicityValueAtTime(sound, time):
    script = praat._scripts_dir + "harmonicityGetValueAtTime";
    return praat.runScript(script, [sound, time, praat._sounds_dir])

