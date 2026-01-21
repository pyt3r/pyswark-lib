import unittest
from enum import Enum as _Enum

from pyswark.lib import enum


class TestIsInstanceRelationships(unittest.TestCase):
    """Test isinstance relationships with pyswark.lib.enum.Enum."""

    def test_isinstance_with_pyswark_enum(self):
        """Test isinstance checks with pyswark.lib.enum.Enum."""
        class TestEnum(enum.Enum):
            A = 1

        class TestStdEnum(_Enum):
            A = 1

        # pyswark.lib.enum.Enum instances
        self.assertTrue(isinstance(TestEnum.A, enum.Enum))
        self.assertFalse(isinstance(TestStdEnum.A, enum.Enum))

    def test_isinstance_with_standard_enum(self):
        """Test isinstance checks with standard library enum.Enum."""
        class TestEnum(enum.Enum):
            A = 1

        class TestStdEnum(_Enum):
            A = 1

        # Standard library enum.Enum instances
        self.assertTrue(isinstance(TestEnum.A, _Enum))
        self.assertTrue(isinstance(TestStdEnum.A, _Enum))
