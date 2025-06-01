# Gmail Node

A LangChain-compatible node for Gmail integration that provides email management capabilities through a natural language interface.

## Features

- Send and draft emails
- Read and manage emails
- Create and manage labels
- Create and manage filters
- Organize emails into folders
- Archive and restore emails
- Search emails using Gmail's search syntax

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON file
   - Place the credentials file in a secure location

4. Set up environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

```python
from gmail_node import GmailNode

# Initialize the Gmail node
gmail_node = GmailNode(
    creds_file_path="path/to/credentials.json",
    token_path="path/to/token.json",
    openai_api_key="your-openai-api-key"
)

# Example: Draft an email
response = await gmail_node.draft_email(
    content="Meeting tomorrow at 2 PM",
    recipient="John Doe",
    recipient_email="john@example.com"
)

# Example: Search emails
response = await gmail_node.search_emails(
    query="from:important@example.com after:2024/01/01"
)

# Example: Manage labels
response = await gmail_node.manage_labels(
    action="Create a new label called 'Important' and apply it to all emails from john@example.com"
)

# Example: Manage filters
response = await gmail_node.manage_filters(
    action="Create a filter to automatically archive all emails from newsletter@example.com"
)

# Example: Manage folders
response = await gmail_node.manage_folders(
    action="Create a new folder called 'Work' and move all emails from work@example.com to it"
)

# Example: Manage archives
response = await gmail_node.manage_archive(
    action="Archive all emails older than 30 days from newsletter@example.com"
)
```

## Available Methods

- `draft_email(content, recipient, recipient_email)`: Draft a new email
- `edit_draft(current_draft, changes)`: Edit an existing email draft
- `manage_labels(action)`: Manage Gmail labels
- `manage_filters(action)`: Manage Gmail filters
- `search_emails(query)`: Search for emails using Gmail's search syntax
- `manage_folders(action)`: Manage Gmail folders
- `manage_archive(action)`: Manage archived emails
- `process_request(request)`: Process a custom request using the Gmail agent

## Gmail Search Syntax

The node supports Gmail's search syntax for advanced email searching:

- `from:sender` - Emails from a specific sender
- `to:recipient` - Emails to a specific recipient
- `subject:text` - Emails with specific text in the subject
- `has:attachment` - Emails with attachments
- `after:YYYY/MM/DD` - Emails after a specific date
- `before:YYYY/MM/DD` - Emails before a specific date
- `is:important` - Important emails
- `label:name` - Emails with a specific label

## Security

- Never commit your credentials or API keys to version control
- Store sensitive information in environment variables
- Use secure paths for storing OAuth tokens
- Regularly rotate your API keys and credentials

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 