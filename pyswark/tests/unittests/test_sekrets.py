import unittest
from unittest.mock import patch, MagicMock

from pyswark.sekrets import api, settings


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
