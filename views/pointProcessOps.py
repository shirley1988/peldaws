import praat
from praat import app

@app.route('/pointprocess/number-of-periods/<sound>/<start>/<end>')
def pointProcessGetNumPeriods(sound, start, end):
    script = praat._scripts_dir + "pointProcessGetNumPeriods";
    return praat.runScript(script, [sound, start, end, praat._sounds_dir])

@app.route('/pointprocess/number-of-points/<sound>')
def pointProcessGetNumPoints(sound):
    script = praat._scripts_dir + "pointProcessGetNumPoints";
    return praat.runScript(script, [sound, praat._sounds_dir])

@app.route('/pointprocess/get-jitter/<sound>/<start>/<end>')
def pointProcessGetJitter(sound, start, end):
    script = praat._scripts_dir + "pointProcessGetJitter";
    return praat.runScript(script, [sound, start, end, praat._sounds_dir])

