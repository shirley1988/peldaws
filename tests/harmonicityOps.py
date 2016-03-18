import unittest
import json
from praat import app

class TestHarmonicityOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
        
    def test_harmonicityGetMin(self):
        result = self.app.get("/harmonicity/get-min/Part1.mp3/0/4")
        data = str.strip(result.data)
        self.assertEqual(data, "-227.76725222324222 dB")
        
    def test_harmonicityGetMax(self):
        result = self.app.get("/harmonicity/get-max/Part1.mp3/0/4")
        data = str.strip(result.data)
        self.assertEqual(data, "35.43616648463154 dB")
        
    def test_harmonicityValueAtTime(self):
        result = self.app.get("/harmonicity/value-at-time/Part1.mp3/1.5")
        data = str.strip(result.data)
        self.assertEqual(data, "-200 dB")
