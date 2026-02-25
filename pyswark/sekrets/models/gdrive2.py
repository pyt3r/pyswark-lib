import json
from typing import Union
from pydantic import field_validator
from pyswark.sekrets.models import base


class ClientJson( base.Sekret ):
    """Google service account key shape; validates and normalizes client_json input."""
    type                        : str
    project_id                  : str
    private_key_id              : str
    private_key                 : str
    client_email                : str
    client_id                   : str
    auth_uri                    : str
    token_uri                   : str
    auth_provider_x509_cert_url : str
    client_x509_cert_url        : str
    universe_domain             : str

    @classmethod
    def fromAny( cls, data: Union[ str, dict, "ClientJson" ] ) -> "ClientJson":
        """Normalize str, dict, or ClientJson to a validated ClientJson instance."""

        if isinstance( data, str ):
            data = json.loads( data )

        if isinstance( data, dict ):
            return cls( **data )

        if isinstance( data, ClientJson ):
            return data

        raise TypeError( f"client_json must be str, dict, or ClientJson; got {type(data)}" )

    def extract( self ):
        return self.model_dump_json()


class Sekret( base.Sekret ):
    path                : str
    use_service_account : bool
    client_json         : ClientJson

    @field_validator( "client_json", mode="before" )
    def _client_json( cls, data ):
        return ClientJson.fromAny( data )

    def extract( self ):
        extracted = super().extract()
        extracted['client_json'] = self.client_json.extract()
        return extracted
