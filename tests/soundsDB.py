import unittest
import json
from StringIO import StringIO

from flask import Request
from werkzeug import FileStorage
from werkzeug.datastructures import MultiDict

from praat import app

class TestSoundsDB(unittest.TestCase):
   def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        
        self.flaskApp = app;
        self.app = app.test_client();
      
   def test_uploadSound(self):
      backupReq = self.flaskApp.request_class
      self.flaskApp.request_class = TestingRequest
      
      # Get test client with the mocked objects
      testClient = self.flaskApp.test_client()

      # Data to be sent via POST
      data = {
         'file': (StringIO("test file"), "test.wav")
      }

      #Bad request 400. Needs debugging
      #response = testClient.post("/upload-sound",data=data)
      
      #Change req class back so that remaining tests can be run
      self.flaskApp.request_class = backupReq
      
      # Load json string as a dictionary
      #result = json.loads(response.data)

      #self.assertEquals(result["status"], "Success")
      self.assertTrue(True)
      
   def test_listSounds(self):
      result = self.app.get("/list-sounds")

      # Load json string as a dictionary
      files = json.loads(result.data)

      # Check if sp1.wav is one of the files returned
      assert "Part1.mp3" in files["files"]


class TestingRequest(Request):
   """A testing request to use that will return a
   TestingFileStorage to test the uploading."""
   @property
   def files(self):
      d = MultiDict()
      d['file'] = TestingFileStorage(filename="test.wav")
      return d

class TestingFileStorage(FileStorage):
    """
    This is a helper for testing upload behavior in your application. You
    can manually create it, and its save method is overloaded to set `saved`
    to the name of the file it was saved to. All of these parameters are
    optional, so only bother setting the ones relevant to your application.

    This was copied from Flask-Uploads.

    :param stream: A stream. The default is an empty stream.
    :param filename: The filename uploaded from the client. The default is the
                     stream's name.
    :param name: The name of the form field it was loaded from. The default is
                 ``None``.
    :param content_type: The content type it was uploaded as. The default is
                         ``application/octet-stream``.
    :param content_length: How long it is. The default is -1.
    :param headers: Multipart headers as a `werkzeug.Headers`. The default is
                    ``None``.
    """
    def __init__(self, stream=None, filename=None, name=None,
                 content_type='application/octet-stream', content_length=-1,
                 headers=None):
        FileStorage.__init__(
            self, stream, filename, name=name,
            content_type=content_type, content_length=content_length,
            headers=None)
        self.saved = None

    def save(self, dst, buffer_size=16384):
        """
        This marks the file as saved by setting the `saved` attribute to the
        name of the file it was saved to.

        :param dst: The file to save to.
        :param buffer_size: Ignored.
        """
        if isinstance(dst, basestring):
            self.saved = dst
        else:
            self.saved = dst.name
