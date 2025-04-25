import unittest

from pyswark.lib.enum import AliasEnum


class SettingsTests( unittest.TestCase ):
    def test_alias_member_of_settings_enum(self):
        alias = 'this-is.a.terrible name for an alias of "a"'
        class Settings( AliasEnum ):
            A       = 1
            A_alias = A, [ alias, 'a' ]

        self.assertEqual( Settings.A.value, 1)
        self.assertEqual( Settings.getMember( Settings.A ).value, 1)
        self.assertEqual( Settings.getMember( alias ).value, 1)

    def test_duplicate_alias(self):

        with self.assertRaises( ValueError ):
            class Settings( AliasEnum ):
                A       = 1
                A_alias = A, [ 'A', 'a' ]
