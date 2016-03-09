import unittest
import json
from praat import app

class TestHarmonicityOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
        
    def test_harmonicityGetMin(self):
        result = self.app.get("/harmonicity/get-min/sp1.wav/0/4")
        data = str.strip(result.data)
        self.assertEqual(data, "-226.4005801205003 dB")
        
    def test_harmonicityGetMax(self):
        result = self.app.get("/harmonicity/get-max/sp1.wav/0/4")
        data = str.strip(result.data)
        self.assertEqual(data, "37.990262670955055 dB")
        
    def test_harmonicityValueAtTime(self):
        result = self.app.get("/harmonicity/value-at-time/sp1.wav/1.5")
        data = str.strip(result.data)
        self.assertEqual(data, "-212.64859235727798 dB")
