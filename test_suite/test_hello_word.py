from pbs.helloword_client import Client
import unittest


class HelloWordCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_resp(self):
        value = self.client.SayHello(params={'name': 's2'})
        print(value)
        self.assertTrue(value)
