import unittest
import json
from praat import app

class TestPitchOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_countVoicedFrames(self):
        result = self.app.get("/pitch/count-voiced-frames/Part1.mp3");
        data = str.strip(result.data)  # Remove trailing newlines
        self.assertEqual(data, "1109 voiced frames")
        
    def test_pitchValueAtTime(self):
        result = self.app.get("/pitch/value-at-time/Part1.mp3/0.5");
        data = str.strip(result.data)
        self.assertEqual(data, "209.77767831353125 Hz")
        
    def test_pitchValueInFrame(self):
        result = self.app.get("/pitch/value-in-frame/Part1.mp3/50");
        data = str.strip(result.data)
        self.assertEqual(data, "209.10986129338275 Hz")
