from PIL import Image

_sound_extensions = set(["wav", "mp3"])

def fileType(fileName):
   return fileName.rsplit('.', 1)[1]

def isSound(fileName):
   return '.' in fileName and \
         fileType(fileName) in _sound_extensions

def resizeImage(image):
   img = Image.open(image)
   img.thumbnail((500,500), Image.ANTIALIAS)
   img.save(image, "PNG", quality=88)

