import unittest
import json
from praat import app

class TestSpectrumOps(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['CSRF_ENABLED'] = False

		self.app = app.test_client()
      
	def test_spectrumFrequencyBounds(self):
		result = self.app.get("/spectrum/get-bounds/Part1.mp3");

                # Load json string as a dictionary
		bounds = json.loads(result.data)

		self.assertEqual(bounds["low"], 0)
		self.assertEqual(bounds["high"], 22050)
