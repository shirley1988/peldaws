import unittest
import json
from praat import app

class TestPointProcessOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()

    def test_pointProcessGetNumPeriods(self):
        result = self.app.get("/pointprocess/number-of-periods/sp1.wav/0/4");
        data = str.strip(result.data)
        self.assertEqual(data, "422")

    def test_pointProcessGetNumPoints(self):
        result = self.app.get("/pointprocess/number-of-points/sp1.wav");
        data = str.strip(result.data)
        self.assertEqual(data, "436")

    def test_pointProcessGetJitter(self):
        result = self.app.get("/pointprocess/get-jitter/sp1.wav/0/4");
        data = str.strip(result.data)
        self.assertEqual(data, "0.021874018562006974")
