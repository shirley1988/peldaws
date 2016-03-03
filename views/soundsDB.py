from flask import jsonify, request
from werkzeug import secure_filename
import os

import utils
import praat
from praat import app

@app.route('/upload-sound', methods=['POST'])
def uploadSound():
   sound = request.files['sound']
   if not sound or not sound.filename:
      status = "No sound file"
      soundName = ""
   elif not utils.isSound(sound.filename):
      status = "Unknown file type"
      soundName = secure_filename(sound.filename)
   else:
      filename = secure_filename(sound.filename)
      sound.save(os.path.join(praat._sounds_dir, filename))
      status = "Success"
      soundName = filename

   result = {
      "status": status,
      "sound": soundName
   }
   return jsonify(result)

@app.route('/list-sounds')
def listSounds():
   response = {
      "files": os.listdir(praat._sounds_dir)
   }
   return jsonify(response)
