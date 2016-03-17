import praat
from praat import app

@app.route('/pitch/count-voiced-frames/<sound>')
def countVoicedFrames(sound):
    script = praat._scripts_dir + "countVoicedFrames";
    return praat.runScript(script, [sound, praat._sounds_dir])

@app.route('/pitch/value-at-time/<sound>/<time>')
def pitchValueAtTime(sound, time):
    script = praat._scripts_dir + "pitchValueAtTime";
    return praat.runScript(script, [sound, time, praat._sounds_dir])

@app.route('/pitch/value-in-frame/<sound>/<frame>')
def pitchValueInFrame(sound, frame):
    script = praat._scripts_dir + "pitchValueInFrame";
    return praat.runScript(script, [sound, frame, praat._sounds_dir])

