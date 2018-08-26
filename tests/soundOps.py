import unittest
import json
from praat import app

class TestSoundOps(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
      
    def test_drawSound(self):
        result = self.app.get("/draw-sound/Part1.mp3/0/4/?pitch&pulse&formants&spectrogram&pulses")
        self.assertEqual(result.content_type, "image/png")

    def test_getBounds(self):
        result = self.app.get("/get-bounds/Part1.mp3")

        # Load json string as a dictionary
        bounds = json.loads(result.data)

        self.assertEquals(bounds["start"], 0.0)
        self.assertEquals(bounds["end"], 25.037256235827666)
        
    def test_getEnergy(self):
        result = self.app.get("/get-energy/Part1.mp3")
        assert "0.07201807012373347 Pa2 sec" in result.data

    def test_playSound(self):
        result = self.app.get("/play/sp1.wav")
        # Check if file being downloaded is a wav audio
        self.assertEqual(result.content_type, "audio/wav")

        result = self.app.get("/play/Part1.mp3")
        # Check if file being downloaded is an mp3 audio
        self.assertEqual(result.content_type, "audio/mp3")

    def test_drawElan(self):
        result = self.app.get("/draw-elan/sp1.wav/1/4/")
        self.assertEqual(result.content_type, "image/png")

    def test_annotationTimeSelection(self):
        result = self.app.get("/annotation/time-selection/sp1.wav/TimeSubdivision-lt/1/4/tetst/test2/test3")
        data = str.strip(result.data)
        self.assertEqual(data, "sp1")
