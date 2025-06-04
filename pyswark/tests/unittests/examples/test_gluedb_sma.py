import unittest
from pyswark.examples.gluedb import sma


class TestGluedbSma(unittest.TestCase):
    def test_smoke_test(self):
        sma.main()