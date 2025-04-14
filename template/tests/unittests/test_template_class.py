import unittest
from template.template_class import TemplateClass


class Test(unittest.TestCase):

    def test_template_class(self):
        o = TemplateClass(1, 2)
        assert o.template_method() == 3


if __name__ == '__main__':
    unittest.main()
