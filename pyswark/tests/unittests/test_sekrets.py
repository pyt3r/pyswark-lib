import unittest
from unittest.mock import patch, MagicMock

from pyswark.sekrets import api, settings
#from pyswark.sekrets.intake import Intake, ingest, toSekretRecords


class TestSekrets(unittest.TestCase):
    """Test the sekrets API functionality with mocked data"""
    
    def setUp(self):
        """Set up test data based on example-iac.json"""
        self.test_data = [
            {
                "info": {
                    "name": "A"
                },
                "body": {
                    "model": "pyswark.sekrets.models.generic.Contents",
                    "contents": {
                        "sekret": "this is the data for A",
                        "description": "description for A"
                    }
                }
            },
            {
                "info": {
                    "name": "B"
                },
                "body": {
                    "model": "pyswark.sekrets.models.generic.Contents",
                    "contents": {
                        "sekret": "this is the data for B",
                        "description": "description for B"
                    }
                }
            },
        ]
    
    @patch('pyswark.sekrets.api.getHub')
    @patch('pyswark.sekrets.api._getProtocolName')
    def test_get_sekret_for_user_A(self, mock_get_protocol, mock_get_hub):
        """Test getting a secret for user 'A'"""
        # Mock the hub and database chain
        mock_hub = MagicMock()
        mock_db = MagicMock()
        mock_get_hub.return_value = mock_hub
        mock_hub.extract.return_value = mock_db
        
        # Mock the database to return the test data for user 'A'
        expected_result = {
            "sekret": "this is the data for A",
            "description": "description for A"
        }
        mock_db.extract.return_value = expected_result
        
        # Mock the protocol name
        mock_get_protocol.return_value = "example-iac"
        
        # Test the get function
        result = api.get("A", settings.Settings.EXAMPLE_IAC.name)
        
        # Verify the result
        self.assertEqual(result, expected_result)
        self.assertEqual(result["sekret"], "this is the data for A")
        self.assertEqual(result["description"], "description for A")

@unittest.skip("Skipping intake tests for now")
class TestIntake(unittest.TestCase):
    """Test the Intake class for ingesting and converting data"""

    def test_ingest_dict(self):
        """Test ingesting a raw dictionary"""
        data = {
            "A": "this is the data for A",
            "B": "this is the data for B",
        }
        intake = Intake.ingest(data)
        self.assertEqual(intake.raw, data)
        self.assertIsNone(intake.source)

    def test_ingest_list_of_tuples(self):
        """Test ingesting a list of key-value tuples"""
        data = [
            ("db_password", "secret123"),
            ("api_key", "xyz-abc-789"),
        ]
        intake = Intake.ingest(data)
        self.assertEqual(intake.raw, {"db_password": "secret123", "api_key": "xyz-abc-789"})

    def test_asSekretRecords_from_dict(self):
        """Test converting dict to sekret records format"""
        data = {
            "A": "this is the data for A",
            "B": "this is the data for B",
        }
        intake = Intake.ingest(data)
        records = intake.asSekretRecords()
        
        self.assertEqual(len(records), 2)
        
        # Check structure of first record
        record_a = next(r for r in records if r["info"]["name"] == "A")
        self.assertEqual(record_a["info"]["name"], "A")
        self.assertEqual(record_a["body"]["model"], "pyswark.sekrets.models.generic.Contents")
        self.assertEqual(record_a["body"]["contents"]["sekret"], "this is the data for A")

    def test_toSekretRecords_shorthand(self):
        """Test the toSekretRecords convenience function"""
        data = [
            ("db_password", "secret123"),
            ("api_key", "xyz-abc-789"),
        ]
        records = toSekretRecords(data)
        
        self.assertEqual(len(records), 2)
        
        record_db = next(r for r in records if r["info"]["name"] == "db_password")
        self.assertEqual(record_db["body"]["contents"]["sekret"], "secret123")

    def test_asGlueDb(self):
        """Test converting to a queryable GlueDb"""


    def test_toJson(self):
        """Test JSON serialization"""
        import json
        
        data = {"A": "value_A"}
        intake = Intake.ingest(data)
        json_output = intake.toJson()
        
        # Parse and verify
        parsed = json.loads(json_output)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["info"]["name"], "A")
        self.assertEqual(parsed[0]["body"]["contents"]["sekret"], "value_A")

    def test_ingest_function(self):
        """Test the ingest convenience function"""
        data = {"key": "value"}
        intake = ingest(data)
        self.assertIsInstance(intake, Intake)
        self.assertEqual(intake.raw, data)
