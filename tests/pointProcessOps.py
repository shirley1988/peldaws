import unittest
import json
from praat import app

class TestPointProcessOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_pointProcessGetNumPeriods(self):
        result = self.app.get("/pointprocess/number-of-periods/Part1.mp3/0/4");
        data = str.strip(result.data) # Remove trailing newlines
        self.assertEqual(data, "194")

    def test_pointProcessGetNumPoints(self):
        result = self.app.get("/pointprocess/number-of-points/Part1.mp3");
        data = str.strip(result.data)
        self.assertEqual(data, "2112")

    def test_pointProcessGetJitter(self):
        result = self.app.get("/pointprocess/get-jitter/Part1.mp3/0/4");
        data = str.strip(result.data)
        self.assertEqual(data, "0.030631749514574105")
