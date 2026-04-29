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
from datetime import datetime
from typing import List
from pyswark.lib.pydantic import base
from pyswark.core.models import body


class SampleModel(base.BaseModel):
    """A sample model for testing Body functionality."""
    a: int
    b: str


class DatetimeModel(base.BaseModel):
    """A sample model with a non-JSON-native field (datetime)."""
    when: datetime
    label: str


class NestedDatetimeModel(base.BaseModel):
    """A model whose nested records carry datetime fields."""
    items: List[DatetimeModel]


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

    def test_sqlmodel_roundtrip(self):
        """
        Body converts to SQLModel and back, preserving the wrapped model.
        
        The full roundtrip:
        1. Pydantic Body wraps a model
        2. Convert to SQLModel (for DB storage)
        3. Convert back to Pydantic Body
        4. Extract the original model type
        """
        # Wrap a model in Body
        original_data = SampleModel(a=99, b='database')
        original_body = body.Body(model=original_data)
        
        # Convert to SQLModel
        sql_model = original_body.asSQLModel()
        self.assertIsInstance(sql_model, body.BodySQLModel)
        self.assertEqual(sql_model.model, original_body.model)
        self.assertEqual(sql_model.contents, original_body.contents)
        
        # Convert back to Pydantic
        restored_body = sql_model.asModel()
        self.assertIsInstance(restored_body, body.Body)
        
        # Extract inner model - still works!
        extracted = restored_body.extract()
        self.assertIsInstance(extracted, SampleModel)
        self.assertEqual(extracted.a, 99)
        self.assertEqual(extracted.b, 'database')


class TestBodyWithNonJsonNativeFields(unittest.TestCase):
    """
    Regression tests: Body must round-trip pydantic models whose fields aren't
    JSON-native (datetime, UUID, Path, ...). The serializer ToDictModel uses
    ``model_dump(mode='json')`` so json.dumps can take it from there.
    """

    def test_datetime_field_roundtrips(self):
        when = datetime(2023, 4, 1, 13, 45, 30)
        original = DatetimeModel(when=when, label='opening day')

        wrapped = body.Body(model=original)
        self.assertIsInstance(wrapped.contents, str)

        extracted = wrapped.extract()
        self.assertIsInstance(extracted, DatetimeModel)
        self.assertEqual(extracted.when, when)
        self.assertEqual(extracted.label, 'opening day')

    def test_nested_datetime_roundtrips_via_json(self):
        nested = NestedDatetimeModel(items=[
            DatetimeModel(when=datetime(2023, 4, 1), label='a'),
            DatetimeModel(when=datetime(2023, 4, 2), label='b'),
        ])

        wrapped = body.Body(model=nested)
        json_str = wrapped.toJson()
        restored = body.Body.fromJson(json_str)
        extracted = restored.extract()

        self.assertIsInstance(extracted, NestedDatetimeModel)
        self.assertEqual(len(extracted.items), 2)
        self.assertEqual(extracted.items[0].when, datetime(2023, 4, 1))
        self.assertEqual(extracted.items[1].label, 'b')


if __name__ == '__main__':
    unittest.main()

