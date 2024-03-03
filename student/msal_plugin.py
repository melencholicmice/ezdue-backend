import json
from msal import ConfidentialClientApplication
from core.exceptions.base import UnimplementedError

class MsLoginPlugin:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
        )

    def get_auth_url(self):
        raise UnimplementedError()

    def get_access_token(self):
        raise UnimplementedError()

    def get_profile_data():
        raise UnimplementedError()

    def validate_profile_data():
        raise UnimplementedError()

