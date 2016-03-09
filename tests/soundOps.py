import unittest
import json
from praat import app

class TestSoundOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
      
    def test_drawSound(self):
        result = self.app.get("/draw-sound/sp1.wav/0/4/?pitch&pulse&formants&spectrogram&pulses")
        self.assertEqual(result.content_type, "image/png")

    def test_getBounds(self):
        result = self.app.get("/get-bounds/sp1.wav")
        bounds = json.loads(result.data)

        self.assertEquals(bounds["start"], 0.0)
        self.assertEquals(bounds["end"], 4.0)
        
    def test_getEnergy(self):
        result = self.app.get("/get-energy/sp1.wav")
        assert "0.002112626523245126 Pa2 sec" in result.data

    def test_playSound(self):
        result = self.app.get("/play/sp1.wav")
        self.assertEqual(result.content_type, "audio/wav")
