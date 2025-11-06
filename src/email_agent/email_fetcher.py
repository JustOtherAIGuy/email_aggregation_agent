"""
Email Fetcher Module

Handles fetching emails from Gmail API.
Provides methods to query and retrieve messages based on various criteria.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class EmailFetcher:
    """
    Fetches emails from Gmail API based on various query parameters.

    Supports date-based queries, label filtering, and result limits.
    """

    def __init__(self, gmail_service):
        """
        Initialize email fetcher with Gmail service.

        Args:
            gmail_service: Authenticated Gmail API service instance
        """
        self.service = gmail_service

    def fetch_messages(
        self,
        days_back: int = 7,
        max_results: int = 50,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Fetch messages from Gmail based on criteria.

        Args:
            days_back: Number of days to look back for messages
            max_results: Maximum number of messages to fetch
            query: Custom Gmail query string (optional)
            label_ids: List of label IDs to filter by (optional)

        Returns:
            List of message dictionaries with id and threadId
        """
        # Build query string
        if query is None:
            query = self.build_date_query(days_back)
        else:
            # Add date filter to custom query if days_back specified
            if days_back:
                date_query = self.build_date_query(days_back)
                query = f"{query} {date_query}"

        # Prepare request parameters
        request_params = {
            'userId': 'me',
            'q': query,
            'maxResults': max_results
        }

        if label_ids:
            request_params['labelIds'] = label_ids

        # Execute request
        try:
            results = self.service.users().messages().list(**request_params).execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []

    def fetch_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Fetch a specific message by its ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Full message object from Gmail API
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            return message
        except Exception as e:
            print(f"Error fetching message {message_id}: {e}")
            return {}

    def build_date_query(self, days_back: int = 7) -> str:
        """
        Build a Gmail query string for date filtering.

        Args:
            days_back: Number of days to look back

        Returns:
            Query string in format "after:YYYY/MM/DD"
        """
        date_filter = datetime.now() - timedelta(days=days_back)
        date_string = date_filter.strftime('%Y/%m/%d')
        return f'after:{date_string}'

    def fetch_unread_messages(
        self,
        days_back: int = 7,
        max_results: int = 50
    ) -> List[Dict[str, str]]:
        """
        Fetch only unread messages.

        Args:
            days_back: Number of days to look back
            max_results: Maximum number of messages

        Returns:
            List of unread message dictionaries
        """
        query = 'is:unread'
        return self.fetch_messages(
            days_back=days_back,
            max_results=max_results,
            query=query
        )

    def fetch_from_sender(
        self,
        sender_email: str,
        days_back: int = 30,
        max_results: int = 50
    ) -> List[Dict[str, str]]:
        """
        Fetch messages from a specific sender.

        Args:
            sender_email: Email address of sender
            days_back: Number of days to look back
            max_results: Maximum number of messages

        Returns:
            List of message dictionaries from sender
        """
        query = f'from:{sender_email}'
        return self.fetch_messages(
            days_back=days_back,
            max_results=max_results,
            query=query
        )

    def fetch_by_subject(
        self,
        subject: str,
        days_back: int = 30,
        max_results: int = 50
    ) -> List[Dict[str, str]]:
        """
        Fetch messages with subject containing specific text.

        Args:
            subject: Text to search for in subject
            days_back: Number of days to look back
            max_results: Maximum number of messages

        Returns:
            List of matching message dictionaries
        """
        query = f'subject:{subject}'
        return self.fetch_messages(
            days_back=days_back,
            max_results=max_results,
            query=query
        )
