"""
Unit tests for email fetching and parsing

TDD Approach: Write tests first, implement later
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import base64


class TestEmailFetcher:
    """Test email fetching functionality"""

    def test_email_fetcher_class_exists(self):
        """Test that EmailFetcher class can be imported"""
        from src.email_agent.email_fetcher import EmailFetcher
        assert EmailFetcher is not None

    def test_email_fetcher_initialization(self):
        """Test EmailFetcher initializes with Gmail service"""
        from src.email_agent.email_fetcher import EmailFetcher

        mock_service = Mock()
        fetcher = EmailFetcher(gmail_service=mock_service)

        assert fetcher is not None
        assert fetcher.service == mock_service

    def test_fetch_messages_by_date(self, sample_email_list):
        """Test fetching messages from specific date range"""
        from src.email_agent.email_fetcher import EmailFetcher

        mock_service = Mock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': sample_email_list
        }

        fetcher = EmailFetcher(gmail_service=mock_service)
        messages = fetcher.fetch_messages(days_back=7)

        assert len(messages) == 3
        assert messages[0]['id'] == 'msg_001'

    def test_fetch_messages_with_max_results(self):
        """Test limiting number of fetched messages"""
        from src.email_agent.email_fetcher import EmailFetcher

        mock_service = Mock()
        mock_list = mock_service.users().messages().list
        mock_list().execute.return_value = {
            'messages': [{'id': f'msg_{i}'} for i in range(10)]
        }

        fetcher = EmailFetcher(gmail_service=mock_service)
        messages = fetcher.fetch_messages(max_results=10)

        # Verify maxResults parameter was passed
        call_args = mock_list.call_args
        assert call_args.kwargs['maxResults'] == 10
        assert len(messages) == 10

    def test_fetch_messages_with_query(self):
        """Test fetching messages with custom query"""
        from src.email_agent.email_fetcher import EmailFetcher

        mock_service = Mock()
        mock_list = mock_service.users().messages().list
        mock_list().execute.return_value = {'messages': []}

        fetcher = EmailFetcher(gmail_service=mock_service)
        fetcher.fetch_messages(query='label:inbox unread')

        # Verify query was passed correctly
        call_args = mock_list.call_args
        assert 'q' in call_args.kwargs
        assert 'label:inbox unread' in call_args.kwargs['q']

    def test_fetch_messages_handles_empty_results(self):
        """Test handling of no messages found"""
        from src.email_agent.email_fetcher import EmailFetcher

        mock_service = Mock()
        mock_service.users().messages().list().execute.return_value = {}

        fetcher = EmailFetcher(gmail_service=mock_service)
        messages = fetcher.fetch_messages()

        assert messages == []

    def test_build_date_query(self):
        """Test building date query string"""
        from src.email_agent.email_fetcher import EmailFetcher

        fetcher = EmailFetcher(gmail_service=Mock())
        query = fetcher.build_date_query(days_back=7)

        assert 'after:' in query
        # Query should contain a date in YYYY/MM/DD format
        assert query.count('/') == 2


class TestEmailParser:
    """Test email parsing functionality"""

    def test_email_parser_class_exists(self):
        """Test that EmailParser class can be imported"""
        from src.email_agent.email_parser import EmailParser
        assert EmailParser is not None

    def test_parse_message_basic(self, sample_gmail_message):
        """Test parsing basic message structure"""
        from src.email_agent.email_parser import EmailParser

        parser = EmailParser()
        parsed = parser.parse_message(sample_gmail_message)

        assert parsed['id'] == 'test_message_123'
        assert parsed['subject'] == 'AI Weekly: Latest Developments'
        assert parsed['sender'] == 'newsletter@example.com'

    def test_extract_headers(self, sample_gmail_message):
        """Test extracting email headers"""
        from src.email_agent.email_parser import EmailParser

        parser = EmailParser()
        headers = parser.extract_headers(sample_gmail_message['payload']['headers'])

        assert headers['subject'] == 'AI Weekly: Latest Developments'
        assert headers['from'] == 'newsletter@example.com'
        assert 'date' in headers

    def test_extract_body_plain_text(self):
        """Test extracting plain text body"""
        from src.email_agent.email_parser import EmailParser

        test_text = "This is a test email body"
        encoded_body = base64.urlsafe_b64encode(test_text.encode()).decode()

        payload = {
            'body': {
                'data': encoded_body
            }
        }

        parser = EmailParser()
        body = parser.extract_body(payload)

        assert body == test_text

    def test_extract_body_multipart(self):
        """Test extracting body from multipart message"""
        from src.email_agent.email_parser import EmailParser

        test_text = "Multipart email content"
        encoded_body = base64.urlsafe_b64encode(test_text.encode()).decode()

        payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': encoded_body}
                },
                {
                    'mimeType': 'text/html',
                    'body': {'data': 'aHRtbCBjb250ZW50'}
                }
            ]
        }

        parser = EmailParser()
        body = parser.extract_body(payload)

        assert test_text in body

    def test_extract_body_handles_missing_data(self):
        """Test handling missing body data"""
        from src.email_agent.email_parser import EmailParser

        payload = {'body': {}}

        parser = EmailParser()
        body = parser.extract_body(payload)

        assert body == ""

    def test_decode_base64_body(self):
        """Test decoding base64 encoded body"""
        from src.email_agent.email_parser import EmailParser

        test_text = "Test message with special chars: héllo wørld! 你好"
        encoded = base64.urlsafe_b64encode(test_text.encode()).decode()

        parser = EmailParser()
        decoded = parser.decode_body(encoded)

        assert decoded == test_text

    def test_clean_html_content(self):
        """Test cleaning HTML from email content"""
        from src.email_agent.email_parser import EmailParser

        html_content = """
        <html>
            <body>
                <h1>Newsletter Title</h1>
                <p>This is a paragraph.</p>
                <a href="http://example.com">Link</a>
            </body>
        </html>
        """

        parser = EmailParser()
        clean_text = parser.clean_html(html_content)

        assert 'Newsletter Title' in clean_text
        assert 'This is a paragraph' in clean_text
        assert '<html>' not in clean_text
        assert '<p>' not in clean_text

    def test_extract_urls_from_content(self):
        """Test extracting URLs from email content"""
        from src.email_agent.email_parser import EmailParser

        content = """
        Check out these links:
        https://example.com/article1
        Visit http://test.com for more info
        """

        parser = EmailParser()
        urls = parser.extract_urls(content)

        assert len(urls) >= 2
        assert 'https://example.com/article1' in urls
        assert 'http://test.com' in urls

    def test_parse_date_string(self):
        """Test parsing email date strings"""
        from src.email_agent.email_parser import EmailParser

        date_str = "Mon, 6 Nov 2025 10:00:00 -0800"

        parser = EmailParser()
        parsed_date = parser.parse_date(date_str)

        assert isinstance(parsed_date, datetime)
        assert parsed_date.year == 2025
        assert parsed_date.month == 11
        assert parsed_date.day == 6

    def test_calculate_email_metadata(self, sample_gmail_message):
        """Test calculating email metadata (word count, length, etc.)"""
        from src.email_agent.email_parser import EmailParser

        parser = EmailParser()
        parsed = parser.parse_message(sample_gmail_message)
        metadata = parser.calculate_metadata(parsed)

        assert 'word_count' in metadata
        assert 'char_count' in metadata
        assert 'has_attachments' in metadata
        assert isinstance(metadata['word_count'], int)


class TestEmailFetcherIntegration:
    """Integration tests for complete email fetching workflow"""

    @pytest.mark.integration
    def test_fetch_and_parse_workflow(self, sample_gmail_message, sample_email_list):
        """Test complete workflow: fetch -> parse"""
        from src.email_agent.email_fetcher import EmailFetcher
        from src.email_agent.email_parser import EmailParser

        # Setup mock service
        mock_service = Mock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': sample_email_list
        }
        mock_service.users().messages().get().execute.return_value = sample_gmail_message

        # Fetch emails
        fetcher = EmailFetcher(gmail_service=mock_service)
        messages = fetcher.fetch_messages(days_back=1)

        # Parse emails
        parser = EmailParser()
        parsed_messages = [parser.parse_message(sample_gmail_message) for _ in messages]

        assert len(parsed_messages) == 3
        assert all('subject' in msg for msg in parsed_messages)
        assert all('body' in msg for msg in parsed_messages)

    @pytest.mark.integration
    def test_batch_processing(self):
        """Test batch processing multiple emails efficiently"""
        from src.email_agent.email_fetcher import EmailFetcher
        from src.email_agent.email_parser import EmailParser

        mock_service = Mock()
        fetcher = EmailFetcher(gmail_service=mock_service)
        parser = EmailParser()

        # This would test batch processing in real scenario
        # For now, just verify the classes work together
        assert fetcher is not None
        assert parser is not None
