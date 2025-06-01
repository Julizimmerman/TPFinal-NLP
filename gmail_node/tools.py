import asyncio
from typing import List, Dict, Any, Optional
from langchain.tools import Tool, StructuredTool
from gmail_node.gmail_service import GmailService

def create_gmail_tools(gmail_service: GmailService) -> List[Tool]:
    """Creates a list of LangChain tools from GmailService methods."""
    
    tools = [
        StructuredTool(
            name="send-email",
            func=lambda recipient_id, subject, message: asyncio.run(
                gmail_service.send_email(recipient_id, subject, message)
            ),
            description="Send an email to a given recipient with subject and body.",
            args_schema={
                "type": "object",
                "properties": {
                    "recipient_id": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "message": {
                        "type": "string",
                        "description": "Email content text",
                    },
                },
                "required": ["recipient_id", "subject", "message"],
            },
        ),
        Tool(
            name="get-unread-emails",
            func=lambda _: asyncio.run(gmail_service.get_unread_emails()),
            description="Retrieve unread emails from the inbox. Returns the count of unread emails and their details.",
        ),
        StructuredTool(
            name="read-email",
            func=lambda email_id: asyncio.run(gmail_service.read_email(email_id)),
            description="Read the content of a specific email.",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to read",
                    },
                },
                "required": ["email_id"],
            },
        ),
        StructuredTool(
            name="create-draft",
            func=lambda recipient_id, subject, message: asyncio.run(
                gmail_service.create_draft(recipient_id, subject, message)
            ),
            description="Create a draft email without sending it.",
            args_schema={
                "type": "object",
                "properties": {
                    "recipient_id": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "message": {
                        "type": "string",
                        "description": "Email content text",
                    },
                },
                "required": ["recipient_id", "subject", "message"],
            },
        ),
        Tool(
            name="list-drafts",
            func=lambda _: asyncio.run(gmail_service.list_drafts()),
            description="List all draft emails.",
        ),
        StructuredTool(
            name="trash-email",
            func=lambda email_id: asyncio.run(gmail_service.trash_email(email_id)),
            description="Move an email to trash.",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to trash",
                    },
                },
                "required": ["email_id"],
            },
        ),
        StructuredTool(
            name="archive-email",
            func=lambda email_id: asyncio.run(gmail_service.archive_email(email_id)),
            description="Archive an email (remove from inbox without deleting).",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to archive",
                    },
                },
                "required": ["email_id"],
            },
        ),
        Tool(
            name="list-labels",
            func=lambda _: asyncio.run(gmail_service.list_labels()),
            description="List all labels in the mailbox.",
        ),
        StructuredTool(
            name="create-label",
            func=lambda name: asyncio.run(gmail_service.create_label(name)),
            description="Create a new label.",
            args_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the new label",
                    },
                },
                "required": ["name"],
            },
        ),
        StructuredTool(
            name="apply-label",
            func=lambda email_id, label_id: asyncio.run(
                gmail_service.apply_label(email_id, label_id)
            ),
            description="Apply a label to an email.",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to label",
                    },
                    "label_id": {
                        "type": "string",
                        "description": "Label ID to apply",
                    },
                },
                "required": ["email_id", "label_id"],
            },
        ),
        StructuredTool(
            name="search-emails",
            func=lambda query, max_results=50: asyncio.run(
                gmail_service.search_emails(query, max_results)
            ),
            description="Search for emails using Gmail's search syntax.",
            args_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                    },
                },
                "required": ["query"],
            },
        ),
        StructuredTool(
            name="create-filter",
            func=lambda **kwargs: asyncio.run(gmail_service.create_filter(**kwargs)),
            description="Create a new email filter.",
            args_schema={
                "type": "object",
                "properties": {
                    "from_email": {
                        "type": "string",
                        "description": "Filter emails from this sender",
                    },
                    "to_email": {
                        "type": "string",
                        "description": "Filter emails to this recipient",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Filter emails with this subject",
                    },
                    "query": {
                        "type": "string",
                        "description": "Filter emails matching this query",
                    },
                    "has_attachment": {
                        "type": "boolean",
                        "description": "Filter emails with attachments",
                    },
                    "exclude_chats": {
                        "type": "boolean",
                        "description": "Exclude chats from filter",
                    },
                    "size_comparison": {
                        "type": "string",
                        "description": "Size comparison ('larger' or 'smaller')",
                    },
                    "size": {
                        "type": "integer",
                        "description": "Size in bytes for comparison",
                    },
                    "add_label_ids": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Labels to add to matching emails",
                    },
                    "remove_label_ids": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Labels to remove from matching emails",
                    },
                    "forward_to": {
                        "type": "string",
                        "description": "Email address to forward matching emails to",
                    },
                },
            },
        ),
        Tool(
            name="list-filters",
            func=lambda _: asyncio.run(gmail_service.list_filters()),
            description="List all email filters.",
        ),
        StructuredTool(
            name="create-folder",
            func=lambda name: asyncio.run(gmail_service.create_folder(name)),
            description="Create a new folder (implemented as a label).",
            args_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the new folder",
                    },
                },
                "required": ["name"],
            },
        ),
        StructuredTool(
            name="move-to-folder",
            func=lambda email_id, folder_id: asyncio.run(
                gmail_service.move_to_folder(email_id, folder_id)
            ),
            description="Move an email to a folder.",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to move",
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "Folder ID to move to",
                    },
                },
                "required": ["email_id", "folder_id"],
            },
        ),
        Tool(
            name="list-folders",
            func=lambda _: asyncio.run(gmail_service.list_folders()),
            description="List all user-created folders.",
        ),
        StructuredTool(
            name="batch-archive",
            func=lambda query, max_emails=100: asyncio.run(
                gmail_service.batch_archive(query, max_emails)
            ),
            description="Archive multiple emails matching a search query.",
            args_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query to find emails to archive",
                    },
                    "max_emails": {
                        "type": "integer",
                        "description": "Maximum number of emails to archive",
                    },
                },
                "required": ["query"],
            },
        ),
        StructuredTool(
            name="list-archived",
            func=lambda max_results=50: asyncio.run(
                gmail_service.list_archived(max_results)
            ),
            description="List archived emails (not in inbox).",
            args_schema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                    },
                },
            },
        ),
        StructuredTool(
            name="restore-to-inbox",
            func=lambda email_id: asyncio.run(gmail_service.restore_to_inbox(email_id)),
            description="Restore an archived email back to the inbox.",
            args_schema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email ID to restore",
                    },
                },
                "required": ["email_id"],
            },
        ),
    ]
    
    return tools 