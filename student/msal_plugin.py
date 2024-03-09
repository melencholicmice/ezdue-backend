import json
import requests
from msal import ConfidentialClientApplication
from core.exceptions.base import UnimplementedError
from student.models import Student

class MsLoginPlugin:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
        )
        self.SCOPES = ['User.Read']

    def get_auth_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': ' '.join(self.SCOPES)
        }
        authorization_url = self.client.get_authorization_request_url(**params)
        return authorization_url

    def get_access_token(self,authorization_code):
        try:
            token_response = self.client.acquire_token_by_authorization_code(code=authorization_code, scopes=self.SCOPES)
            access_token = token_response.get('access_token')
            return access_token
        except Exception as e:
            return e

    def get_profile_data(self,access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def validate_profile_data(self,user_data):
        email = user_data.get('mail')
        if email:
            try:
                student = Student.objects.get(email=email)
                return True
            except Student.DoesNotExist:
                return False
        else:
            return False


