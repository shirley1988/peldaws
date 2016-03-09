import unittest
import json
from praat import app

class TestFormantOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_formantFrameCount(self):
        result = self.app.get("/formant/number-of-frames/sp1.wav");
        data = str.strip(result.data)
        self.assertEqual(data, "632 frames")
        
    def test_formantCountAtFrame(self):
        result = self.app.get("/formant/number-of-formants/sp1.wav/50");
        data = str.strip(result.data)
        self.assertEqual(data, "3 formants")
        
    def test_formantValueAtTime(self):
        result = self.app.get("/formant/value-at-time/sp1.wav/1/1.5");
        data = str.strip(result.data)
        self.assertEqual(data, "1246.9708704631173 Hertz")
