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

    def test_apidocs(self):
        result = self.app.get("/apidocs")
        assert "<html>" in result.data
