import praat
from praatWS import app

@app.route('/pitch/countVoicedFrames/<sound>')
def countVoicedFrames(sound):
    script = praat._scripts_dir + "countVoicedFrames";
    return praat.runScript(script, [sound, praat._sounds_dir])

@app.route('/pitch/valueAtTime/<sound>/<time>')
def pitchValueAtTime(sound, time):
    script = praat._scripts_dir + "pitchValueAtTime";
    return praat.runScript(script, [sound, time, praat._sounds_dir])

@app.route('/pitch/valueInFrame/<sound>/<frame>')
def pitchValueInFrame(sound, frame):
    script = praat_scripts_dir + "pitchValueInFrame";
    return praat.runScript(script, [sound, frame, praat._sounds_dir])


