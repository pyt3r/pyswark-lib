import unittest

from pyswark.core import settings


class SettingsTests( unittest.TestCase ):
    def test_alias_member_of_settings_enum(self):
        alias = 'this-is.a.terrible name for an alias of "a"'
        class Settings( settings.Settings ):
            A       = 1
            A_alias = ( alias, A )

        self.assertEqual( Settings.A.value, 1)
        self.assertEqual( Settings.getMember( Settings.A ).value, 1)
        self.assertEqual( Settings.getMember( alias ).value, 1)

