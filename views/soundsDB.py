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

        # Before saving, check if we are replacing an existing sound
        existingSounds = getSoundArray()
        if filename in existingSounds:
            # If sound changes, cached images become invalid
            utils.deleteCachedImages(praat._images_dir, filename)             

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

def getSoundArray():
    """ Return list of available sounds as an array """
    return os.listdir(praat._sounds_dir)

@app.route('/list-sounds')
def listSounds():
    """ Get a list of sound files available, as a JSON String """
    response = {
            "files": getSoundArray()
    }
    return jsonify(response)

