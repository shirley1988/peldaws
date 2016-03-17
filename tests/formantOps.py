import unittest
import json
from praat import app

class TestFormantOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_formantFrameCount(self):
        result = self.app.get("/formant/number-of-frames/Part1.mp3");
        data = str.strip(result.data)
        self.assertEqual(data, "3998 frames")
        
    def test_formantCountAtFrame(self):
        result = self.app.get("/formant/number-of-formants/Part1.mp3/50");
        data = str.strip(result.data)
        self.assertEqual(data, "5 formants")
        
    def test_formantValueAtTime(self):
        result = self.app.get("/formant/value-at-time/Part1.mp3/1/1.5");
        data = str.strip(result.data)
        self.assertEqual(data, "1270.2346757852933 Hertz")
