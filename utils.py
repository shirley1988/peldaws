from PIL import Image
import os, re
import errno
import hashlib
import uuid

# Supported audio types.
# To add a format already supported by praat, just add the extension here
_sound_extensions = set(["wav", "mp3"])

def fileType(fileName):
   """ Return file extension """
   return fileName.rsplit('.', 1)[1]

def isSound(fileName):
   """ Checks if fileName has a valid sound file extension """
   return '.' in fileName and \
         fileType(fileName) in _sound_extensions

def resizeImage(image):
   """ Down-scaling the image to 500x500 pixels """
   img = Image.open(image)
   img.thumbnail((500,500), Image.ANTIALIAS)
   img.save(image, "PNG", quality=88)

def deleteCachedImages(directory, prefix):
   """ Delete cached images starting with prefix """
   pattern = "^" + prefix + ".*"
   for f in os.listdir(directory):
       if re.search(pattern, f):
           os.remove(os.path.join(directory, f))

def normalize(string):
    return re.sub('[^0-9a-zA-Z]+', '_', string).lower()

def personal_group_name(user):
    return normalize(user.name + " personal group" + user.id)

def generate_id(seed=None):
    if isinstance(seed, basestring):
        return hashlib.md5(str(seed)).hexdigest()
    return str(uuid.uuid4()).replace('-', '')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def is_true(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, basestring):
        return str(v).lower() == 'true' or str(v) == '1'
    return v == 1
