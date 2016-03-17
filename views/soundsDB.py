from flask import jsonify, request
from werkzeug import secure_filename
import os

import utils
import praat
from praat import app

@app.route('/upload-sound', methods=['POST'])
def uploadSound():
    # Get uploaded sound file   
    sound = request.files['sound']

    if not sound or not sound.filename:
        # If no sound file, stop
        status = "No sound file"
        soundName = ""
    elif not utils.isSound(sound.filename):
        # Stop if uploaded file is not a sound
        status = "Unknown file type"
        soundName = secure_filename(sound.filename)
    else:
        # Remove path modifiers or unsafe characters from filename
        filename = secure_filename(sound.filename)

        # Save file to disk
        sound.save(os.path.join(praat._sounds_dir, filename))

        status = "Success"
        soundName = filename

    # Return status and the filename used
    # Sound name may be different than the one provided by the user
    result = {
        "status": status,
        "sound": soundName
    }
    return jsonify(result)

@app.route('/list-sounds')
def listSounds():
    # Get a list of sound files available, as a JSON String
    response = {
            "files": os.listdir(praat._sounds_dir)
    }
    return jsonify(response)

