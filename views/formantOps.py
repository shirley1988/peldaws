import praat
from praat import app

@app.route('/formant/number-of-frames/<sound>')
def formantFrameCount(sound):
    script = praat._scripts_dir + "formantFrameCount";
    return praat.runScript(script, [sound, praat._sounds_dir])

@app.route('/formant/number-of-formants/<sound>/<frame>')
def formantCountAtFrame(sound, frame):
    script = praat._scripts_dir + "formantCount";
    return praat.runScript(script, [sound, frame, praat._sounds_dir])

@app.route('/formant/value-at-time/<sound>/<formantNumber>/<time>')
def formantValueAtTime(sound, formantNumber, time):
    script = praat._scripts_dir + "formantValueAtTime";
    return praat.runScript(script, [sound, formantNumber, time, praat._sounds_dir])

