import unittest
import os
import pyswark
from pyswark.infra.init import dumpPackageData
from pyswark.infra.init import get_version
from pyswark.util.log import logger


class TestCase(unittest.TestCase):

    def test_package_data(self):
        package = pyswark
        package_data = dumpPackageData(package.__file__)
        basedir = os.path.dirname(package.__file__)
        for fn in package_data[package.__name__]:
            if '*' not in fn:
                filepath = os.path.join(basedir, fn)
                logger.debug(filepath)
                assert os.path.exists(filepath)
            else:
                logger.debug(fn)

    def test_get_version(self):
        assert pyswark.__version__ == get_version(pyswark.__file__)
