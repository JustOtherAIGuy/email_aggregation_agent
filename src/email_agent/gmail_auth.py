"""
Gmail Authentication Module

Handles OAuth2 authentication for Gmail API access.
Implements credential management, token refresh, and service initialization.
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAuth:
    """
    Manages Gmail API authentication and authorization.

    Handles OAuth2 flow, token storage, and Gmail service creation.
    """

    DEFAULT_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        scopes: Optional[List[str]] = None
    ):
        """
        Initialize Gmail authentication handler.

        Args:
            credentials_path: Path to credentials.json from Google Cloud Console
            token_path: Path to store/load the access token
            scopes: List of Gmail API scopes to request
        """
        self.credentials_path = credentials_path or os.getenv(
            'GMAIL_CREDENTIALS_PATH',
            './credentials.json'
        )
        self.token_path = token_path or os.getenv(
            'GMAIL_TOKEN_PATH',
            './token.json'
        )
        self.scopes = scopes or self.DEFAULT_SCOPES
        self._credentials: Optional[Credentials] = None
        self._service = None

    @classmethod
    def from_env(cls) -> 'GmailAuth':
        """
        Create GmailAuth instance from environment variables.

        Returns:
            GmailAuth instance configured from environment
        """
        return cls(
            credentials_path=os.getenv('GMAIL_CREDENTIALS_PATH'),
            token_path=os.getenv('GMAIL_TOKEN_PATH')
        )

    def get_credentials(self) -> Credentials:
        """
        Get valid credentials, handling refresh and new auth flow.

        Returns:
            Valid Google OAuth2 credentials

        Raises:
            FileNotFoundError: If credentials.json not found and no valid token exists
        """
        # Try to load existing credentials
        if self._credentials and self._credentials.valid:
            return self._credentials

        # Load from token file if exists
        if Path(self.token_path).exists():
            self._credentials = Credentials.from_authorized_user_file(
                self.token_path,
                self.scopes
            )

        # Refresh expired credentials
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            print("Refreshing expired credentials...")
            self._credentials.refresh(Request())
            self.save_credentials(self._credentials)
            return self._credentials

        # If credentials are valid, return them
        if self._credentials and self._credentials.valid:
            return self._credentials

        # No valid credentials, need to run OAuth flow
        if not Path(self.credentials_path).exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}\n"
                "Please download credentials.json from Google Cloud Console"
            )

        print("Starting new authentication flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            self.scopes
        )

        self._credentials = flow.run_local_server(port=0)
        self.save_credentials(self._credentials)

        return self._credentials

    def save_credentials(self, credentials: Credentials) -> None:
        """
        Save credentials to token file.

        Args:
            credentials: Credentials to save
        """
        token_path = Path(self.token_path)
        token_path.parent.mkdir(parents=True, exist_ok=True)

        with open(token_path, 'w') as f:
            f.write(credentials.to_json())

        print(f"Credentials saved to: {self.token_path}")

    def get_gmail_service(self):
        """
        Get authenticated Gmail API service instance.

        Returns:
            Gmail API service resource
        """
        if self._service:
            return self._service

        credentials = self.get_credentials()
        self._service = build('gmail', 'v1', credentials=credentials)

        return self._service

    def test_connection(self) -> Dict[str, Any]:
        """
        Test Gmail API connection and return account info.

        Returns:
            Dictionary with connection status and account info
        """
        try:
            service = self.get_gmail_service()
            profile = service.users().getProfile(userId='me').execute()

            return {
                'success': True,
                'emailAddress': profile.get('emailAddress'),
                'messagesTotal': profile.get('messagesTotal'),
                'threadsTotal': profile.get('threadsTotal')
            }
        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }
        except Exception as error:
            return {
                'success': False,
                'error': str(error)
            }


def setup_gmail_auth() -> GmailAuth:
    """
    Convenience function to set up Gmail authentication.

    Returns:
        Configured GmailAuth instance
    """
    print("Setting up Gmail authentication...")
    auth = GmailAuth.from_env()

    print("Testing connection...")
    result = auth.test_connection()

    if result['success']:
        print(f"✓ Successfully connected to: {result['emailAddress']}")
        print(f"  Total messages: {result['messagesTotal']}")
    else:
        print(f"✗ Connection failed: {result['error']}")

    return auth
