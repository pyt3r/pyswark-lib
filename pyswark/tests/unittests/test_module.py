import unittest
from pyswark.module import covered


class Test(unittest.TestCase):

    def test_module(self):
        import pyswark
        print('template_package:', pyswark)
        assert covered() is not None


if __name__ == '__main__':
    unittest.main()
