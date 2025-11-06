"""
Pytest configuration and shared fixtures
"""
import os
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List


@pytest.fixture
def sample_gmail_message() -> Dict[str, Any]:
    """Sample Gmail API message structure"""
    return {
        'id': 'test_message_123',
        'threadId': 'thread_123',
        'labelIds': ['INBOX', 'UNREAD'],
        'snippet': 'This is a test newsletter about AI developments...',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'newsletter@example.com'},
                {'name': 'Subject', 'value': 'AI Weekly: Latest Developments'},
                {'name': 'Date', 'value': 'Mon, 6 Nov 2025 10:00:00 -0800'}
            ],
            'body': {
                'data': 'VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keQ=='  # Base64 encoded
            }
        },
        'internalDate': '1699286400000'
    }


@pytest.fixture
def sample_email_list() -> List[Dict[str, str]]:
    """Sample list of email message IDs"""
    return [
        {'id': 'msg_001', 'threadId': 'thread_001'},
        {'id': 'msg_002', 'threadId': 'thread_002'},
        {'id': 'msg_003', 'threadId': 'thread_003'}
    ]


@pytest.fixture
def sample_parsed_email() -> Dict[str, Any]:
    """Sample parsed email content"""
    return {
        'id': 'test_message_123',
        'subject': 'AI Weekly: Latest Developments',
        'sender': 'newsletter@example.com',
        'date': '2025-11-06T10:00:00',
        'body': 'This is a test email body with newsletter content about AI developments.',
        'snippet': 'This is a test newsletter about AI developments...'
    }


@pytest.fixture
def sample_email_analysis() -> Dict[str, Any]:
    """Sample email analysis from agent"""
    return {
        'topic': 'AI Developments',
        'key_points': [
            'New GPT model released',
            'AI safety regulations proposed',
            'Major investment in AI startups'
        ],
        'companies_mentioned': ['OpenAI', 'Anthropic', 'Google'],
        'importance_score': 4,
        'action_items': ['Review new GPT capabilities', 'Monitor regulatory changes']
    }


@pytest.fixture
def mock_gmail_service(mocker):
    """Mock Gmail API service"""
    mock_service = mocker.Mock()
    mock_service.users().messages().list().execute.return_value = {
        'messages': [
            {'id': 'msg_001'},
            {'id': 'msg_002'}
        ]
    }
    return mock_service


@pytest.fixture
def azure_openai_config() -> Dict[str, str]:
    """Sample Azure OpenAI configuration"""
    return {
        'model': 'gpt-4',
        'api_type': 'azure',
        'api_key': 'test_api_key',
        'base_url': 'https://test.openai.azure.com/',
        'api_version': '2024-02-15-preview'
    }


@pytest.fixture
def temp_checkpoint_dir(tmp_path):
    """Temporary directory for checkpoints"""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    return checkpoint_dir


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, tmp_path):
    """Set up test environment variables"""
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", str(tmp_path / "credentials.json"))
    monkeypatch.setenv("GMAIL_TOKEN_PATH", str(tmp_path / "token.json"))
