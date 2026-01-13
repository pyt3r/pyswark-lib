"""
Tests for pyswark.core.models.info
==================================

Info is a lightweight metadata container for records.
It stores basic information like name.

Example Usage
-------------
>>> from pyswark.core.models import info
>>> obj = info.Info(name='my_data')
>>> obj.name
'my_data'
"""

import unittest
from pyswark.core.models import info


class TestInfo(unittest.TestCase):
    """Tests for Info model - the metadata container for records."""

    def test_create_info_with_name(self):
        """
        Create an Info object with a name.
        
        Info is the simplest model - just a name for identifying records.
        """
        obj = info.Info(name='stock_prices')
        
        self.assertEqual(obj.name, 'stock_prices')

    def test_info_serialization_roundtrip(self):
        """
        Info objects can be serialized to JSON and restored.
        
        The serialized form includes type information, enabling
        automatic deserialization without specifying the class.
        """
        # Create and serialize
        original = info.Info(name='market_data')
        json_str = original.toJson()
        
        # Deserialize (no type hint needed!)
        restored = info.Info.fromJson(json_str)
        
        self.assertEqual(restored.name, original.name)
        self.assertIsInstance(restored, info.Info)

    def test_info_from_dict(self):
        """
        Info can be created from a dictionary.
        
        Useful when loading from configuration files or APIs.
        """
        data = {'name': 'config_settings'}
        obj = info.Info(**data)
        
        self.assertEqual(obj.name, 'config_settings')

    def test_sqlmodel_roundtrip(self):
        """
        Info converts to SQLModel and back without data loss.
        
        This enables seamless transition between:
        - Pydantic models (validation, serialization)
        - SQLModel tables (database persistence)
        """
        # Create Pydantic model
        original = info.Info(name='db_record')
        
        # Convert to SQLModel (for database storage)
        sql_model = original.asSQLModel()
        self.assertIsInstance(sql_model, info.InfoSQLModel)
        self.assertEqual(sql_model.name, 'db_record')
        
        # Convert back to Pydantic (for business logic)
        restored = sql_model.asModel()
        self.assertIsInstance(restored, info.Info)
        self.assertEqual(restored.name, original.name)


if __name__ == '__main__':
    unittest.main()

