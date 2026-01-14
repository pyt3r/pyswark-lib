"""
Tests for pyswark.core.models.mixin
===================================

TypeCheck provides utilities for runtime type validation using
string-based class paths. This enables "late binding" - you can
reference types by their path and resolve them at runtime.

This is foundational for the pyswark "code as data" pattern where
class references are stored as strings (URIs) and dynamically imported.

Example Usage
-------------
>>> from pyswark.core.models.mixin import TypeCheck
>>> from pyswark.lib.pydantic import base
>>>
>>> # Import a type from its string path
>>> BaseModel = TypeCheck.importType('pyswark.lib.pydantic.base.BaseModel')
>>>
>>> # Check if two types are the same
>>> TypeCheck.isSameType(base.BaseModel, 'pyswark.lib.pydantic.base.BaseModel')
True
"""

import unittest
from pyswark.core.models.mixin import TypeCheck
from pyswark.lib.pydantic import base


class ParentModel(base.BaseModel):
    """A parent model for inheritance tests."""
    name: str


class ChildModel(ParentModel):
    """A child model inheriting from ParentModel."""
    age: int


class UnrelatedModel(base.BaseModel):
    """An unrelated model for negative tests."""
    value: float


class TestTypeCheck(unittest.TestCase):
    """Tests for TypeCheck - runtime type validation utilities."""

    def test_import_type_from_string(self):
        """
        TypeCheck.importType() resolves string paths to actual types.
        
        This is the foundation of late-binding - store class paths as
        strings in configs/databases, then import them at runtime.
        """
        # Import using the string path
        imported = TypeCheck.importType('pyswark.lib.pydantic.base.BaseModel')
        
        # Should be the actual class
        self.assertIs(imported, base.BaseModel)

    def test_import_type_passthrough(self):
        """
        TypeCheck.importType() passes through actual types unchanged.
        
        This enables uniform handling - you can pass either a string
        path or the type itself, and get consistent behavior.
        """
        # Pass an actual type
        result = TypeCheck.importType(ParentModel)
        
        # Should return the same type
        self.assertIs(result, ParentModel)

    def test_is_same_type(self):
        """
        TypeCheck.isSameType() compares types, accepting strings or types.
        
        Useful for validation when you have a mix of string paths
        and actual type references.
        """
        # Compare type to itself
        self.assertTrue(TypeCheck.isSameType(ParentModel, ParentModel))
        
        # Compare type to its string path
        parent_uri = ParentModel.getUri()
        self.assertTrue(TypeCheck.isSameType(ParentModel, parent_uri))
        
        # Different types should not match
        self.assertFalse(TypeCheck.isSameType(ParentModel, ChildModel))

    def test_is_subclass(self):
        """
        TypeCheck.isSubclass() checks inheritance, accepting strings or types.
        
        Essential for validating that a provided type meets interface
        requirements (e.g., "must inherit from BaseModel").
        """
        # ChildModel inherits from ParentModel
        self.assertTrue(TypeCheck.isSubclass(ChildModel, ParentModel))
        
        # Both inherit from BaseModel
        base_uri = base.BaseModel.getUri()
        self.assertTrue(TypeCheck.isSubclass(ParentModel, base_uri))
        self.assertTrue(TypeCheck.isSubclass(ChildModel, base_uri))
        
        # ParentModel is not a subclass of ChildModel
        self.assertFalse(TypeCheck.isSubclass(ParentModel, ChildModel))
        
        # Unrelated models don't have subclass relationship
        self.assertFalse(TypeCheck.isSubclass(UnrelatedModel, ParentModel))

    def test_is_instance(self):
        """
        TypeCheck.isInstance() checks instances, accepting string type paths.
        
        Allows instance checking against string-based type specifications,
        useful when types are configured externally.
        """
        parent = ParentModel(name='Alice')
        child = ChildModel(name='Bob', age=25)
        
        # Direct instance checks
        self.assertTrue(TypeCheck.isInstance(parent, ParentModel))
        self.assertTrue(TypeCheck.isInstance(child, ChildModel))
        
        # Child is also an instance of Parent (inheritance)
        self.assertTrue(TypeCheck.isInstance(child, ParentModel))
        
        # Check against string path
        parent_uri = ParentModel.getUri()
        self.assertTrue(TypeCheck.isInstance(parent, parent_uri))
        
        # Negative case
        self.assertFalse(TypeCheck.isInstance(parent, ChildModel))

    def test_check_if_allowed_type(self):
        """
        TypeCheck.checkIfAllowedType() validates against an allow list.
        
        Enables "type whitelisting" - ensure only approved types are used
        in certain contexts (e.g., only specific model types in a database).
        """
        allowed = [ParentModel.getUri(), ChildModel.getUri()]
        
        # Should pass for allowed types
        TypeCheck.checkIfAllowedType(ParentModel, allowed)  # No exception
        TypeCheck.checkIfAllowedType(ChildModel.getUri(), allowed)  # String works too
        
        # Should raise for disallowed type
        with self.assertRaises(ValueError) as ctx:
            TypeCheck.checkIfAllowedType(UnrelatedModel, allowed)
        
        self.assertIn('is not an allowed type', str(ctx.exception))

    def test_check_if_subclass_raises(self):
        """
        TypeCheck.checkIfSubclass() raises ValueError for non-subclasses.
        
        Use as a guard clause to enforce inheritance requirements.
        """
        # Should pass
        TypeCheck.checkIfSubclass(ChildModel, ParentModel)  # No exception
        
        # Should raise
        with self.assertRaises(ValueError) as ctx:
            TypeCheck.checkIfSubclass(ParentModel, ChildModel)
        
        self.assertIn('is not a subclass', str(ctx.exception))

    def test_check_if_instance_raises(self):
        """
        TypeCheck.checkIfInstance() raises ValueError for non-instances.
        
        Use as a guard clause to enforce type requirements.
        """
        parent = ParentModel(name='Test')
        
        # Should pass
        TypeCheck.checkIfInstance(parent, ParentModel)  # No exception
        
        # Should raise
        with self.assertRaises(ValueError) as ctx:
            TypeCheck.checkIfInstance(parent, ChildModel)
        
        self.assertIn('is not an instance', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()

