import unittest
import json
from praat import app

class TestHTML(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False

        self.app = app.test_client()
        
    def test_index(self):
        result = self.app.get("/")
        assert "<html>" in result.data

    def test_Praatapidocs(self):
        result = self.app.get("/Praatapidocs")
        assert "<html>" in result.data

    def test_ELANapidocs(self):
        result = self.app.get("/ELANapidocs")
        assert "<html>" in result.data
