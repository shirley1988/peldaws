from flask import jsonify, request, g
from flask_login import login_required
from werkzeug import secure_filename
import os

import utils
import praat
from praat import app

@app.route('/upload-sound', methods=['POST'])
@login_required
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
        user = g.user
        group = praat.Group.query.get(user.current_group_id)
        subdir = "%s/%s/%s" % (praat._sounds_dir, group.id, 'audios')
        utils.mkdir_p(subdir)
        # Before saving, check if we are replacing an existing sound
        # TODO: handle it later
        # existingSounds = getSoundArray(group=group)
        #if filename in existingSounds:
            # If sound changes, cached images become invalid
            #utils.deleteCachedImages(praat._images_dir, filename)

        # Save file to disk
        sound.save(os.path.join(subdir, filename))

        status = "Success"
        soundName = filename

    # Return status and the filename used
    # Sound name may be different than the one provided by the user
    result = {
        "status": status,
        "sound": soundName
    }
    return jsonify(result)

def getSoundArray(group=None):
    """ Return list of available sounds as an array """
    subdir = praat._sounds_dir
    if group is not None:
        subdir = os.path.join(subdir, group.id, 'audios')
    return [f for f in os.listdir(subdir)
            if os.path.isfile(os.path.join(subdir, f))]

@app.route('/list-sounds')
def listSounds():
    """ Get a list of sound files available, as a JSON String """
    user = g.user
    group = praat.Group.query.get(user.current_group_id)
    response = {
            "files": getSoundArray(group)
    }
    return jsonify(response)
