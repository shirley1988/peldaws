import unittest
import json
from praat import app

class TestIntensityOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
        
    def test_intensityBounds(self):
        result = self.app.get("/intensity/get-bounds/Part1.mp3")

        # Load json string as a dictionary
        bounds = json.loads(result.data)
        
        self.assertEqual(bounds["min"], 33.26029304246234)
        self.assertEqual(bounds["max"], 81.3878316773733)
        self.assertEqual(bounds["mean"], 68.5621161178694)
        
    def test_intensityMean(self):
        result = self.app.get("/intensity/get-mean/Part1.mp3/1/2")
        data = str.strip(result.data) # Remove trailing spaces or newlines
        self.assertEqual(data, "39.27050907778324 dB")

    def test_intensityValueAtTime(self):
        result = self.app.get("intensity/value-at-time/Part1.mp3/0.5")
        data = str.strip(result.data)
        self.assertEqual(data, "59.809381823146246 dB")

