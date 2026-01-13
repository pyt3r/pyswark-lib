"""
Tests for pyswark.core.models.body
==================================

Body wraps any Pydantic model, storing it as a serialized string.
This enables storing arbitrary models in a uniform structure.

The key pattern: Body accepts either:
- A dict with 'model' (class path) and 'contents' (data)
- A Pydantic BaseModel instance directly

Example Usage
-------------
>>> from pyswark.lib.pydantic import base
>>> from pyswark.core.models import body
>>>
>>> class MyModel(base.BaseModel):
...     value: int
>>>
>>> obj = MyModel(value=42)
>>> wrapped = body.Body(model=obj)
>>> extracted = wrapped.extract()
>>> extracted.value
42
"""

import unittest
from pyswark.lib.pydantic import base
from pyswark.core.models import body


class SampleModel(base.BaseModel):
    """A sample model for testing Body functionality."""
    a: int
    b: str


class TestBody(unittest.TestCase):
    """Tests for Body model - the universal model wrapper."""

    def test_wrap_model_instance(self):
        """
        Body can wrap any Pydantic BaseModel instance.
        
        When you pass a model instance, Body automatically:
        1. Extracts the model's class path
        2. Serializes the contents to JSON string
        """
        # Create a model instance
        model = SampleModel(a=1, b='hello')
        
        # Wrap it in Body
        wrapped = body.Body(model=model)
        
        # Body stores the class path and serialized contents
        self.assertIn('SampleModel', wrapped.model)
        self.assertIsInstance(wrapped.contents, str)  # JSON string

    def test_extract_restores_original_model(self):
        """
        Body.extract() reconstructs the original model.
        
        This is the core "code as data" pattern - serialize a model,
        store/transmit it, then reconstruct the exact same type.
        """
        # Create and wrap
        original = SampleModel(a=42, b='world')
        wrapped = body.Body(model=original)
        
        # Extract back to original type
        extracted = wrapped.extract()
        
        self.assertIsInstance(extracted, SampleModel)
        self.assertEqual(extracted.a, 42)
        self.assertEqual(extracted.b, 'world')

    def test_body_serialization_roundtrip(self):
        """
        Body itself can be serialized and restored.
        
        This enables storing wrapped models in databases, files,
        or transmitting over networks.
        """
        # Create wrapped model
        model = SampleModel(a=100, b='test')
        wrapped = body.Body(model=model)
        
        # Serialize Body to JSON
        json_str = wrapped.toJson()
        
        # Restore Body from JSON
        restored_body = body.Body.fromJson(json_str)
        
        # Extract the inner model
        extracted = restored_body.extract()
        
        self.assertEqual(extracted.a, 100)
        self.assertEqual(extracted.b, 'test')

    def test_body_from_explicit_dict(self):
        """
        Body can be created with explicit model path and contents.
        
        Useful when you know the class path and have raw data.
        """
        model_path = SampleModel.getUri()
        contents = {'a': 5, 'b': 'explicit'}
        
        wrapped = body.Body(model=model_path, contents=contents)
        extracted = wrapped.extract()
        
        self.assertEqual(extracted.a, 5)
        self.assertEqual(extracted.b, 'explicit')


if __name__ == '__main__':
    unittest.main()

