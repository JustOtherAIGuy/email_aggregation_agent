"""
Email Parser Module

Parses Gmail API message objects into clean, structured format.
Handles base64 decoding, HTML cleaning, and metadata extraction.
"""
import base64
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.utils import parsedate_to_datetime

import html2text


class EmailParser:
    """
    Parses Gmail API message objects into structured format.

    Handles various email formats, encodings, and MIME types.
    """

    def __init__(self):
        """Initialize email parser with HTML to text converter."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_emphasis = False

    def parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse complete message into structured format.

        Args:
            message: Gmail API message object

        Returns:
            Dictionary with parsed email content
        """
        # Extract message ID and thread
        message_id = message.get('id', '')
        thread_id = message.get('threadId', '')

        # Extract headers
        headers = self.extract_headers(message.get('payload', {}).get('headers', []))

        # Extract body
        body = self.extract_body(message.get('payload', {}))

        # Parse date
        date_str = headers.get('date', '')
        parsed_date = self.parse_date(date_str) if date_str else None

        return {
            'id': message_id,
            'thread_id': thread_id,
            'subject': headers.get('subject', 'No Subject'),
            'sender': headers.get('from', 'Unknown'),
            'to': headers.get('to', ''),
            'date': parsed_date.isoformat() if parsed_date else '',
            'body': body,
            'snippet': message.get('snippet', '')
        }

    def extract_headers(self, headers: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Extract common headers into dictionary.

        Args:
            headers: List of header dictionaries from Gmail API

        Returns:
            Dictionary mapping header names to values
        """
        header_dict = {}
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            header_dict[name] = value

        return header_dict

    def extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from payload, handling various MIME types.

        Args:
            payload: Email payload from Gmail API

        Returns:
            Extracted text content
        """
        # Check if body is directly in payload
        if 'body' in payload and 'data' in payload['body']:
            body_data = payload['body']['data']
            if body_data:
                return self.decode_body(body_data)

        # Check for multipart message
        if 'parts' in payload:
            return self._extract_from_parts(payload['parts'])

        return ""

    def _extract_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        """
        Extract body from multipart message.

        Args:
            parts: List of message parts

        Returns:
            Combined text content
        """
        texts = []

        for part in parts:
            mime_type = part.get('mimeType', '')

            # Handle nested parts
            if 'parts' in part:
                texts.append(self._extract_from_parts(part['parts']))
                continue

            # Extract text/plain or text/html
            if mime_type in ['text/plain', 'text/html']:
                if 'data' in part.get('body', {}):
                    body_data = part['body']['data']
                    decoded = self.decode_body(body_data)

                    # Convert HTML to text if needed
                    if mime_type == 'text/html':
                        decoded = self.clean_html(decoded)

                    texts.append(decoded)

        return '\n\n'.join(filter(None, texts))

    def decode_body(self, encoded_body: str) -> str:
        """
        Decode base64 URL-safe encoded body.

        Args:
            encoded_body: Base64 encoded string

        Returns:
            Decoded text
        """
        try:
            # Gmail uses URL-safe base64 encoding
            decoded_bytes = base64.urlsafe_b64decode(encoded_body)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error decoding body: {e}")
            return ""

    def clean_html(self, html_content: str) -> str:
        """
        Convert HTML to clean text.

        Args:
            html_content: HTML string

        Returns:
            Plain text version
        """
        try:
            return self.html_converter.handle(html_content)
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return html_content

    def extract_urls(self, content: str) -> List[str]:
        """
        Extract URLs from email content.

        Args:
            content: Email text content

        Returns:
            List of URLs found
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        return urls

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse email date string to datetime object.

        Args:
            date_str: Date string from email header

        Returns:
            Parsed datetime object or None
        """
        try:
            return parsedate_to_datetime(date_str)
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return None

    def calculate_metadata(self, parsed_email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate metadata about email.

        Args:
            parsed_email: Parsed email dictionary

        Returns:
            Dictionary with metadata
        """
        body = parsed_email.get('body', '')
        words = body.split()

        metadata = {
            'word_count': len(words),
            'char_count': len(body),
            'has_attachments': False,  # Would need additional logic
            'url_count': len(self.extract_urls(body)),
            'estimated_read_time_minutes': max(1, len(words) // 200)  # Avg reading speed
        }

        return metadata

    def extract_sender_name(self, sender: str) -> str:
        """
        Extract name from sender field.

        Args:
            sender: Full sender string (e.g., "John Doe <john@example.com>")

        Returns:
            Just the name part
        """
        match = re.match(r'^(.+?)\s*<', sender)
        if match:
            return match.group(1).strip('"')
        return sender

    def extract_sender_email(self, sender: str) -> str:
        """
        Extract email address from sender field.

        Args:
            sender: Full sender string

        Returns:
            Just the email address
        """
        match = re.search(r'<(.+?)>', sender)
        if match:
            return match.group(1)
        # If no brackets, assume entire string is email
        if '@' in sender:
            return sender
        return ""
