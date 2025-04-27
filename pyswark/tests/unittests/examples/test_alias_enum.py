import unittest

from pyswark.examples import alias_enum


class TestAliasEnumExamples( unittest.TestCase ):

    def test_base_enum_behavior(self):
        alias_enum.baseEnumBehavior()

    def test_patched_enum_behavior(self):
        alias_enum.patchedBehavior()
