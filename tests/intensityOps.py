import unittest
import json
from praat import app

class TestIntensityOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
        
    def test_intensityBounds(self):
        result = self.app.get("/intensity/get-bounds/sp1.wav")
        bounds = json.loads(result.data)
        
        self.assertEqual(bounds["min"], 37.36793761863101)
        self.assertEqual(bounds["max"], 68.96113475212057)
        self.assertEqual(bounds["mean"], 61.20009563626668)
        
    def test_intensityMean(self):
        result = self.app.get("/intensity/get-mean/sp1.wav/1/2")
        data = str.strip(result.data)
        self.assertEqual(data, "60.95423608453416 dB")