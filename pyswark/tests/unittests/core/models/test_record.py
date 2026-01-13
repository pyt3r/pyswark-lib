"""
Tests for pyswark.core.models.record
====================================

Record combines Info (metadata) and Body (content) into a complete
data record. This is the fundamental unit for data catalogs.

A Record has:
- info: Metadata like name, timestamps
- body: The wrapped model/data

Example Usage
-------------
>>> from pyswark.core.models import info, body, record
>>> from pyswark.lib.pydantic import base
>>>
>>> class MyData(base.BaseModel):
...     value: int
>>>
>>> data = MyData(value=42)
>>> rec = record.Record(
...     info=info.Info(name='my_record'),
...     body=body.Body(model=data)
... )
"""

import unittest
from pyswark.lib.pydantic import base
from pyswark.core.models import info, body, record


class DataModel(base.BaseModel):
    """Sample data model for testing records."""
    x: int
    y: str


class TestRecord(unittest.TestCase):
    """Tests for Record model - combining metadata and content."""

    def test_create_record_with_objects(self):
        """
        Create a Record from Info and Body objects.
        
        This is the standard way to create a complete record.
        """
        # Create the components
        info_obj = info.Info(name='sensor_data')
        data = DataModel(x=100, y='reading')
        body_obj = body.Body(model=data)
        
        # Combine into a record
        rec = record.Record(info=info_obj, body=body_obj)
        
        self.assertEqual(rec.info.name, 'sensor_data')
        self.assertIsInstance(rec.body, body.Body)

    def test_create_record_from_dicts(self):
        """
        Record can be created from dictionaries (auto-coerced).
        
        Pydantic automatically converts dicts to the appropriate types,
        making it easy to create records from JSON/YAML configs.
        """
        # Create Body first (needed as object for this test)
        data = DataModel(x=50, y='config')
        body_obj = body.Body(model=data)
        
        # Info can be passed as dict
        rec = record.Record(
            info={'name': 'from_dict'},
            body=body_obj
        )
        
        self.assertEqual(rec.info.name, 'from_dict')
        self.assertIsInstance(rec.info, info.Info)

    def test_record_full_serialization_roundtrip(self):
        """
        Complete Record serialization and restoration.
        
        This demonstrates the full "code as data" workflow:
        1. Create a record with typed data
        2. Serialize to JSON (can store/transmit)
        3. Restore the complete record with all types
        4. Extract the original data model
        """
        # Step 1: Create a complete record
        original_data = DataModel(x=42, y='answer')
        original_record = record.Record(
            info=info.Info(name='the_answer'),
            body=body.Body(model=original_data)
        )
        
        # Step 2: Serialize to JSON
        json_str = original_record.toJson()
        
        # Step 3: Restore from JSON
        restored_record = record.Record.fromJson(json_str)
        
        # Verify metadata
        self.assertEqual(restored_record.info.name, 'the_answer')
        
        # Step 4: Extract the inner data model
        extracted_data = restored_record.body.extract()
        
        self.assertIsInstance(extracted_data, DataModel)
        self.assertEqual(extracted_data.x, 42)
        self.assertEqual(extracted_data.y, 'answer')

    def test_record_preserves_type_information(self):
        """
        Records preserve full type information through serialization.
        
        The key insight: after a roundtrip through JSON, we get back
        the exact same Python types - not just dicts.
        """
        # Create with specific types
        data = DataModel(x=1, y='typed')
        rec = record.Record(
            info=info.Info(name='typed_record'),
            body=body.Body(model=data)
        )
        
        # Roundtrip
        json_str = rec.toJson()
        restored = record.Record.fromJson(json_str)
        
        # All types preserved
        self.assertIsInstance(restored, record.Record)
        self.assertIsInstance(restored.info, info.Info)
        self.assertIsInstance(restored.body, body.Body)
        
        # Inner model type also preserved
        extracted = restored.body.extract()
        self.assertIsInstance(extracted, DataModel)


if __name__ == '__main__':
    unittest.main()

