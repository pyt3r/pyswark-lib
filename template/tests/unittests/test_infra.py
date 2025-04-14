import unittest
import os
import template
from template.infra.init import dumpPackageData
from template.infra.init import get_version
from template.util.log import logger


class TestCase(unittest.TestCase):

    def test_package_data(self):
        package = template
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
        assert template.__version__ == get_version(template.__file__)
