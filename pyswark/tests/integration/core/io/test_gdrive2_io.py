import unittest

from pyswark.core.io import api


class TestGDrive2IoIntegration(unittest.TestCase):
    """
    Smoke test for reading via pyswark.core.io.api using a gdrive2 URI.

    No assertions are made; the test simply exercises the path and will
    fail if the integration is broken.
    """

    def test_api_read_gdrive2_uri(self):
        api.read("gdrive2://@phb2114/phb2114-keepme.json")

