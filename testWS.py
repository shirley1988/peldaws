import unittest
import praatWS
import json

class TestPraatWS(unittest.TestCase):
   def setUp(self):
      praatWS.app.config['TESTING'] = True
      self.app = praatWS.app.test_client()

   def test_index(self):
       result = self.app.get("/")
       assert "<html>" in result.data

   def test_drawSound(self):
      result = self.app.get("/drawSound/sp1.wav/0/0/1/1/1")
      self.assertEqual(result.content_type, "image/png")

   def test_getBounds(self):
      result = self.app.get("/getBounds/sp1.wav")
      bounds = json.loads(result.data)

      self.assertEquals(bounds["start"], 0.0)
      self.assertEquals(bounds["end"], 4.0)

   def test_getEnergy(self):
      result = self.app.get("/getEnergy/sp1.wav")
      assert "0.002112626523245126 Pa2 sec" in result.data

   def test_playSound(self):
      result = self.app.get("/play/sp1.wav")
      self.assertEqual(result.content_type, "audio/wav")

if __name__ == "__main__":
   unittest.main()
