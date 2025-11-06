"""
Unit tests for Gmail authentication module

Following TDD: These tests are written FIRST, before implementation.
They should fail initially, then pass after implementation.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from google.oauth2.credentials import Credentials


class TestGmailAuth:
    """Test Gmail authentication functionality"""

    def test_gmail_auth_class_exists(self):
        """Test that GmailAuth class can be imported"""
        from src.email_agent.gmail_auth import GmailAuth
        assert GmailAuth is not None

    def test_gmail_auth_initialization(self):
        """Test GmailAuth initializes with correct scopes"""
        from src.email_agent.gmail_auth import GmailAuth

        auth = GmailAuth()
        assert auth is not None
        assert hasattr(auth, 'scopes')
        assert 'https://www.googleapis.com/auth/gmail.readonly' in auth.scopes

    def test_gmail_auth_custom_scopes(self):
        """Test GmailAuth accepts custom scopes"""
        from src.email_agent.gmail_auth import GmailAuth

        custom_scopes = ['https://www.googleapis.com/auth/gmail.modify']
        auth = GmailAuth(scopes=custom_scopes)
        assert auth.scopes == custom_scopes

    @patch('src.email_agent.gmail_auth.Credentials')
    def test_load_existing_credentials(self, mock_creds, tmp_path):
        """Test loading existing valid credentials"""
        from src.email_agent.gmail_auth import GmailAuth

        # Setup - create token file
        token_path = tmp_path / "token.json"
        token_path.write_text('{"token": "test"}')

        # Create credentials file too
        creds_path = tmp_path / "credentials.json"
        creds_path.write_text('{"installed": {"client_id": "test"}}')

        mock_creds.from_authorized_user_file.return_value = Mock(
            valid=True,
            expired=False
        )

        auth = GmailAuth(
            credentials_path=str(creds_path),
            token_path=str(token_path)
        )
        creds = auth.get_credentials()

        assert creds is not None
        assert creds.valid is True

    @patch('src.email_agent.gmail_auth.Credentials')
    def test_refresh_expired_credentials(self, mock_creds, tmp_path):
        """Test refreshing expired credentials"""
        from src.email_agent.gmail_auth import GmailAuth

        # Setup expired credentials
        token_path = tmp_path / "token.json"
        token_path.write_text('{"token": "old_token"}')

        creds_path = tmp_path / "credentials.json"
        creds_path.write_text('{"installed": {"client_id": "test"}}')

        mock_cred = Mock()
        mock_cred.valid = False
        mock_cred.expired = True
        mock_cred.refresh_token = "refresh_token"
        mock_cred.to_json.return_value = '{"token": "refreshed_token"}'
        mock_creds.from_authorized_user_file.return_value = mock_cred

        auth = GmailAuth(
            credentials_path=str(creds_path),
            token_path=str(token_path)
        )

        with patch('google.auth.transport.requests.Request'):
            creds = auth.get_credentials()
            mock_cred.refresh.assert_called_once()

    @patch('src.email_agent.gmail_auth.InstalledAppFlow')
    def test_new_authentication_flow(self, mock_flow, tmp_path):
        """Test new authentication flow when no token exists"""
        from src.email_agent.gmail_auth import GmailAuth

        # Setup
        creds_path = tmp_path / "credentials.json"
        creds_path.write_text('{"installed": {"client_id": "test"}}')
        token_path = tmp_path / "token.json"

        mock_creds = Mock(valid=True)
        mock_creds.to_json.return_value = '{"token": "new_token"}'

        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        auth = GmailAuth(
            credentials_path=str(creds_path),
            token_path=str(token_path)
        )

        creds = auth.get_credentials()

        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once()

    def test_save_credentials(self, tmp_path):
        """Test saving credentials to file"""
        from src.email_agent.gmail_auth import GmailAuth

        token_path = tmp_path / "token.json"
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"token": "test_token"}'

        auth = GmailAuth(token_path=str(token_path))
        auth.save_credentials(mock_creds)

        assert token_path.exists()
        assert "test_token" in token_path.read_text()

    def test_credentials_path_validation(self):
        """Test that invalid credentials path raises error"""
        from src.email_agent.gmail_auth import GmailAuth

        with pytest.raises(FileNotFoundError):
            auth = GmailAuth(credentials_path="/nonexistent/credentials.json")
            auth.get_credentials()

    @patch('src.email_agent.gmail_auth.build')
    def test_get_gmail_service(self, mock_build, tmp_path):
        """Test getting Gmail service instance"""
        from src.email_agent.gmail_auth import GmailAuth

        mock_service = Mock()
        mock_build.return_value = mock_service

        auth = GmailAuth()
        with patch.object(auth, 'get_credentials', return_value=Mock()):
            service = auth.get_gmail_service()

            assert service is not None
            mock_build.assert_called_once_with(
                'gmail', 'v1', credentials=auth.get_credentials()
            )

    def test_connection_test_success(self):
        """Test successful connection test"""
        from src.email_agent.gmail_auth import GmailAuth

        auth = GmailAuth()
        mock_service = Mock()
        mock_service.users().getProfile().execute.return_value = {
            'emailAddress': 'test@example.com',
            'messagesTotal': 100
        }

        with patch.object(auth, 'get_gmail_service', return_value=mock_service):
            result = auth.test_connection()

            assert result['success'] is True
            assert 'emailAddress' in result
            assert result['emailAddress'] == 'test@example.com'

    def test_connection_test_failure(self):
        """Test connection test failure handling"""
        from src.email_agent.gmail_auth import GmailAuth

        auth = GmailAuth()
        mock_service = Mock()
        mock_service.users().getProfile().execute.side_effect = Exception("Connection failed")

        with patch.object(auth, 'get_gmail_service', return_value=mock_service):
            result = auth.test_connection()

            assert result['success'] is False
            assert 'error' in result


class TestGmailAuthIntegration:
    """Integration tests for Gmail authentication"""

    @pytest.mark.integration
    @pytest.mark.gmail
    def test_full_auth_flow_with_env_vars(self, tmp_path, monkeypatch):
        """Test complete authentication flow using environment variables"""
        from src.email_agent.gmail_auth import GmailAuth

        # Setup environment
        creds_path = tmp_path / "credentials.json"
        token_path = tmp_path / "token.json"

        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", str(creds_path))
        monkeypatch.setenv("GMAIL_TOKEN_PATH", str(token_path))

        # This test would require actual credentials in a real scenario
        # For now, we just verify the configuration is read correctly
        auth = GmailAuth.from_env()

        assert auth.credentials_path == str(creds_path)
        assert auth.token_path == str(token_path)
