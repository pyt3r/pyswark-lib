import unittest
from enum import Enum

from pyswark.lib.aenum import AliasEnum, Alias, AliasEnumError


class MixedBag( AliasEnum ):
    A = 1
    B = 1, Alias('b')

    C = 1, 2
    D = 1, 2, Alias('d')

    E = (1, 2)
    F = (1, 2), Alias('f')

    G = [1, 2]
    H = [1, 2], Alias('h')

    I = Alias('i')


class DuplicateEnum( Enum ):
    C = (1, 2)
    E = (1, 2)

class DuplicateAliasEnum( AliasEnum ):
    C = (1, 2)
    E = (1, 2)


class SettingsTests( unittest.TestCase ):

    def test_each_member_is_unique_and_does_not_use_enums_internal_aliasing(self):
        self.assertIs( DuplicateEnum.C, DuplicateEnum.E )
        self.assertIsNot( DuplicateAliasEnum.C, DuplicateAliasEnum.E )

    def test_ability_to_parse_values_as_base_enum_and_alias_enum(self):
        cases = [
            ( MixedBag.A, "name=A, value=1, aliases=['A']" ),
            ( MixedBag.B, "name=B, value=1, aliases=['B', 'b']" ),
            ( MixedBag.C, "name=C, value=(1, 2), aliases=['C']" ),
            ( MixedBag.D, "name=D, value=[1, 2], aliases=['D', 'd']" ),
            ( MixedBag.E, "name=E, value=(1, 2), aliases=['E']" ),
            ( MixedBag.F, "name=F, value=(1, 2), aliases=['F', 'f']" ),
            ( MixedBag.G, "name=G, value=[1, 2], aliases=['G']" ),
            ( MixedBag.H, "name=H, value=[1, 2], aliases=['H', 'h']" ),
            ( MixedBag.I, "name=I, value=Alias({'i'}), aliases=['I']" ),
        ]
        for i, (test, expected) in enumerate( cases ):
            with self.subTest( i=i, test=test ):
                self.assertEqual( expected, test.__repr__() )

    def test_duplicate_alias(self):
        with self.assertRaises( AliasEnumError ):
            class Settings( AliasEnum ):
                A    = 1
                dupe = A, Alias( 'A', 'a' )


class TestDynamicEnum(unittest.TestCase):

    def test_createDynamically(self):
        e = AliasEnum.createDynamically({'a': 1, '123 this is my variable name': 2})
        self.assertEqual(e.a.value, 1)
        self.assertEqual(e._123_this_is_my_variable_name.value, 2)

    def test_asPythonCode(self):
        e = AliasEnum.createDynamically({'a': 1, '123 this is my variable name': 2})
        code = "from pyswark.lib.enum import AliasEnum"
        code += '\n\n'
        code += 'class MyAliasEnum( AliasEnum ):'
        code += '\n    '
        code += 'a = 1'
        code += '\n    '
        code += '_123_this_is_my_variable_name = 2'

        self.assertEqual(e.asPythonCode(), code )
