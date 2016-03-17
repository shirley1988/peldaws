import unittest
import json
from praat import app

class TestPitchOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_countVoicedFrames(self):
        result = self.app.get("/pitch/count-voiced-frames/sp1.wav");
        data = str.strip(result.data)  # Remove trailing newlines
        self.assertEqual(data, "226 voiced frames")
        
    def test_pitchValueAtTime(self):
        result = self.app.get("/pitch/value-at-time/sp1.wav/0.5");
        data = str.strip(result.data)
        self.assertEqual(data, "168.02776306737476 Hz")
        
    def test_pitchValueInFrame(self):
        result = self.app.get("/pitch/value-in-frame/sp1.wav/50");
        data = str.strip(result.data)
        self.assertEqual(data, "166.0978621084084 Hz")
