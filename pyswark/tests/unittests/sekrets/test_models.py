import json
import unittest

from pyswark.sekrets.models import enum as enum_models
from pyswark.sekrets.models import generic as generic_model
from pyswark.sekrets.models import gdrive2 as gdrive2_model


class TestModelsEnum( unittest.TestCase ):

    def test_enum_values_and_klass(self):
        """Models enum should point to the correct Sekret classes via python:// URIs."""
        self.assertEqual(
            enum_models.Models.GENERIC.value,
            "python://pyswark.sekrets.models.generic.Sekret",
        )
        self.assertEqual(
            enum_models.Models.GDRIVE2.value,
            "python://pyswark.sekrets.models.gdrive2.Sekret",
        )

        # klass should resolve to classes with the expected module and name
        generic_klass = enum_models.Models.GENERIC.klass
        gdrive2_klass = enum_models.Models.GDRIVE2.klass

        self.assertEqual(
            (generic_klass.__module__, generic_klass.__name__),
            (generic_model.Sekret.__module__, generic_model.Sekret.__name__),
        )
        self.assertEqual(
            (gdrive2_klass.__module__, gdrive2_klass.__name__),
            (gdrive2_model.Sekret.__module__, gdrive2_model.Sekret.__name__),
        )


class TestGDrive2Models( unittest.TestCase ):

    def setUp(self):
        self.client_json_dict = {
            "type": "service_account",
            "project_id": "my-project",
            "private_key_id": "key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
            "client_email": "service-account@my-project.iam.gserviceaccount.com",
            "client_id": "1234567890",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account",
            "universe_domain": "googleapis.com",
        }

    def test_clientjson_fromAny_with_dict(self):
        cj = gdrive2_model.ClientJson.fromAny(self.client_json_dict)
        self.assertIsInstance(cj, gdrive2_model.ClientJson)
        self.assertEqual(cj.project_id, self.client_json_dict["project_id"])

    def test_clientjson_fromAny_with_json_string(self):
        data_str = json.dumps(self.client_json_dict)
        cj = gdrive2_model.ClientJson.fromAny(data_str)
        self.assertIsInstance(cj, gdrive2_model.ClientJson)
        self.assertEqual(cj.model_dump(), self.client_json_dict)

    def test_clientjson_fromAny_with_instance(self):
        original = gdrive2_model.ClientJson(**self.client_json_dict)
        cj = gdrive2_model.ClientJson.fromAny(original)
        self.assertIs(cj, original)

    def test_clientjson_fromAny_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            gdrive2_model.ClientJson.fromAny(123)  # type: ignore[arg-type]

    def test_clientjson_extract_returns_json_string(self):
        cj = gdrive2_model.ClientJson(**self.client_json_dict)
        json_str = cj.extract()
        self.assertIsInstance(json_str, str)
        self.assertEqual(json.loads(json_str), cj.model_dump())

    def test_sekret_accepts_dict_client_json(self):
        sekret = gdrive2_model.Sekret(
            path="some/folder",
            use_service_account=True,
            client_json=self.client_json_dict,
        )
        self.assertIsInstance(sekret.client_json, gdrive2_model.ClientJson)
        self.assertEqual(sekret.client_json.project_id, self.client_json_dict["project_id"])

    def test_sekret_accepts_json_string_client_json(self):
        json_str = json.dumps(self.client_json_dict)
        sekret = gdrive2_model.Sekret(
            path="some/folder",
            use_service_account=True,
            client_json=json_str,
        )
        self.assertIsInstance(sekret.client_json, gdrive2_model.ClientJson)

    def test_sekret_extract_serializes_client_json_as_json_string(self):
        sekret = gdrive2_model.Sekret(
            path="some/folder",
            use_service_account=True,
            client_json=self.client_json_dict,
        )
        extracted = sekret.extract()
        self.assertEqual(extracted["path"], "some/folder")
        self.assertTrue(extracted["use_service_account"])
        self.assertIsInstance(extracted["client_json"], str)
        self.assertEqual(
            json.loads(extracted["client_json"]),
            sekret.client_json.model_dump(),
        )

