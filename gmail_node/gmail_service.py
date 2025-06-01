from typing import Any, List, Dict
import os
import asyncio
import logging
import base64
from email.message import EmailMessage
from email.header import decode_header
from base64 import urlsafe_b64decode
from email import message_from_bytes
import webbrowser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_mime_header(header: str) -> str: 
    """Helper function to decode encoded email headers"""
    decoded_parts = decode_header(header)
    decoded_string = ''
    for part, encoding in decoded_parts: 
        if isinstance(part, bytes): 
            decoded_string += part.decode(encoding or 'utf-8') 
        else: 
            decoded_string += part 
    return decoded_string

class GmailService:
    def __init__(self,
                 creds_file_path: str,
                 token_path: str,
                 scopes: list[str] = ['https://www.googleapis.com/auth/gmail.modify']):
        logger.info(f"Initializing GmailService with creds file: {creds_file_path}")
        self.creds_file_path = creds_file_path
        self.token_path = token_path
        self.scopes = scopes
        self.token = self._get_token()
        logger.info("Token retrieved successfully")
        self.service = self._get_service()
        logger.info("Gmail service initialized")
        self.user_email = self._get_user_email()
        logger.info(f"User email retrieved: {self.user_email}")

    def _get_token(self) -> Credentials:
        """Get or refresh Google API token"""
        token = None
    
        if os.path.exists(self.token_path):
            logger.info('Loading token from file')
            token = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                logger.info('Refreshing token')
                token.refresh(Request())
            else:
                logger.info('Fetching new token')
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, self.scopes)
                token = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token_file:
                token_file.write(token.to_json())
                logger.info(f'Token saved to {self.token_path}')

        return token

    def _get_service(self) -> Any:
        """Initialize Gmail API service"""
        try:
            service = build('gmail', 'v1', credentials=self.token)
            return service
        except HttpError as error:
            logger.error(f'An error occurred building Gmail service: {error}')
            raise ValueError(f'An error occurred: {error}')
    
    def _get_user_email(self) -> str:
        """Get user email address"""
        profile = self.service.users().getProfile(userId='me').execute()
        user_email = profile.get('emailAddress', '')
        return user_email
    
    async def send_email(self, recipient_id: str, subject: str, message: str,) -> dict:
        """Creates and sends an email message"""
        try:
            message_obj = EmailMessage()
            message_obj.set_content(message)
            
            message_obj['To'] = recipient_id
            message_obj['From'] = self.user_email
            message_obj['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            send_message = await asyncio.to_thread(
                self.service.users().messages().send(userId="me", body=create_message).execute
            )
            logger.info(f"Message sent: {send_message['id']}")
            return {"status": "success", "message_id": send_message["id"]}
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}

    async def open_email(self, email_id: str) -> str:
        """Opens email in browser given ID."""
        try:
            url = f"https://mail.google.com/#all/{email_id}"
            webbrowser.open(url, new=0, autoraise=True)
            return "Email opened in browser successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"

    async def get_unread_emails(self) -> List[Dict[str, Any]]:
        """Get all unread emails from the inbox."""
        try:
            # Get all unread messages
            query = 'is:unread'  # Removed category:primary restriction
            messages = []
            page_token = None
            
            while True:
                # Get messages with pagination
                result = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=100
                ).execute()
                
                if 'messages' in result:
                    messages.extend(result['messages'])
                
                # Get next page token
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            # Get full message details for each message
            email_list = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg['payload']['headers']
                email_data = {
                    'id': msg['id'],
                    'threadId': msg['threadId'],
                    'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)'),
                    'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown'),
                    'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown'),
                    'snippet': msg.get('snippet', '')
                }
                email_list.append(email_data)
            
            return {
                'count': len(email_list),
                'messages': email_list
            }
            
        except Exception as e:
            logger.error(f"Error getting unread emails: {str(e)}")
            raise

    async def read_email(self, email_id: str) -> dict[str, str]| str:
        """Retrieves email contents including to, from, subject, and contents."""
        try:
            msg = self.service.users().messages().get(userId="me", id=email_id, format='raw').execute()
            email_metadata = {}

            raw_data = msg['raw']
            decoded_data = urlsafe_b64decode(raw_data)
            mime_message = message_from_bytes(decoded_data)

            body = None
            if mime_message.is_multipart():
                for part in mime_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = mime_message.get_payload(decode=True).decode()
            email_metadata['content'] = body
            
            email_metadata['subject'] = decode_mime_header(mime_message.get('subject', ''))
            email_metadata['from'] = mime_message.get('from','')
            email_metadata['to'] = mime_message.get('to','')
            email_metadata['date'] = mime_message.get('date','')
            
            logger.info(f"Email read: {email_id}")
            await self.mark_email_as_read(email_id)

            return email_metadata
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
        
    async def trash_email(self, email_id: str) -> str:
        """Moves email to trash given ID."""
        try:
            self.service.users().messages().trash(userId="me", id=email_id).execute()
            logger.info(f"Email moved to trash: {email_id}")
            return "Email moved to trash successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
        
    async def mark_email_as_read(self, email_id: str) -> str:
        """Marks email as read given ID."""
        try:
            self.service.users().messages().modify(userId="me", id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
            logger.info(f"Email marked as read: {email_id}")
            return "Email marked as read."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def create_draft(self, recipient_id: str, subject: str, message: str) -> dict:
        """Creates a draft email message"""
        try:
            message_obj = EmailMessage()
            message_obj.set_content(message)
            
            message_obj['To'] = recipient_id
            message_obj['From'] = self.user_email
            message_obj['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            draft = await asyncio.to_thread(
                self.service.users().drafts().create(userId="me", body={'message': create_message}).execute
            )
            logger.info(f"Draft created: {draft['id']}")
            return {"status": "success", "draft_id": draft["id"]}
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}
    
    async def list_drafts(self) -> list[dict] | str:
        """Lists all draft emails"""
        try:
            results = await asyncio.to_thread(
                self.service.users().drafts().list(userId="me").execute
            )
            drafts = results.get('drafts', [])
            
            draft_list = []
            for draft in drafts:
                draft_id = draft['id']
                draft_data = await asyncio.to_thread(
                    self.service.users().drafts().get(userId="me", id=draft_id).execute
                )
                
                message = draft_data.get('message', {})
                headers = message.get('payload', {}).get('headers', [])
                
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
                to = next((header['value'] for header in headers if header['name'].lower() == 'to'), 'No Recipient')
                
                draft_list.append({
                    'id': draft_id,
                    'subject': subject,
                    'to': to
                })
                
            return draft_list
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def list_labels(self) -> list[dict] | str:
        """Lists all labels in the user's mailbox"""
        try:
            results = await asyncio.to_thread(
                self.service.users().labels().list(userId="me").execute
            )
            labels = results.get('labels', [])
            
            label_list = []
            for label in labels:
                label_list.append({
                    'id': label['id'],
                    'name': label['name'],
                    'type': label['type']
                })
                
            return label_list
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def create_label(self, name: str) -> dict | str:
        """Creates a new label"""
        try:
            label_object = {
                'name': name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = await asyncio.to_thread(
                self.service.users().labels().create(userId="me", body=label_object).execute
            )
            
            logger.info(f"Label created: {created_label['id']}")
            return {
                'status': 'success',
                'label_id': created_label['id'],
                'name': created_label['name']
            }
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}
    
    async def apply_label(self, email_id: str, label_id: str) -> str:
        """Applies a label to an email"""
        try:
            await asyncio.to_thread(
                self.service.users().messages().modify(
                    userId="me", 
                    id=email_id, 
                    body={'addLabelIds': [label_id]}
                ).execute
            )
            
            logger.info(f"Label {label_id} applied to email {email_id}")
            return f"Label applied successfully to email."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def remove_label(self, email_id: str, label_id: str) -> str:
        """Removes a label from an email"""
        try:
            await asyncio.to_thread(
                self.service.users().messages().modify(
                    userId="me", 
                    id=email_id, 
                    body={'removeLabelIds': [label_id]}
                ).execute
            )
            
            logger.info(f"Label {label_id} removed from email {email_id}")
            return f"Label removed successfully from email."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def search_by_label(self, label_id: str) -> list[dict] | str:
        """Searches for emails with a specific label"""
        try:
            query = f"label:{label_id}"
            
            response = await asyncio.to_thread(
                self.service.users().messages().list(userId="me", q=query).execute
            )
            
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = await asyncio.to_thread(
                    self.service.users().messages().list(
                        userId="me", 
                        q=query,
                        pageToken=page_token
                    ).execute
                )
                messages.extend(response['messages'])
                
            return messages
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def list_filters(self) -> list[dict] | str:
        """Lists all filters in the user's mailbox"""
        try:
            results = await asyncio.to_thread(
                self.service.users().settings().filters().list(userId="me").execute
            )
            filters = results.get('filter', [])
            return filters
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def get_filter(self, filter_id: str) -> dict | str:
        """Gets a specific filter by ID"""
        try:
            filter_data = await asyncio.to_thread(
                self.service.users().settings().filters().get(userId="me", id=filter_id).execute
            )
            return filter_data
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def create_filter(self, 
                           from_email: str = None,
                           to_email: str = None,
                           subject: str = None,
                           query: str = None,
                           has_attachment: bool = None,
                           exclude_chats: bool = None,
                           size_comparison: str = None,
                           size: int = None,
                           add_label_ids: list[str] = None,
                           remove_label_ids: list[str] = None,
                           forward_to: str = None) -> dict | str:
        """Creates a new email filter"""
        try:
            criteria = {}
            if from_email:
                criteria['from'] = from_email
            if to_email:
                criteria['to'] = to_email
            if subject:
                criteria['subject'] = subject
            if query:
                criteria['query'] = query
            if has_attachment is not None:
                criteria['hasAttachment'] = has_attachment
            if exclude_chats is not None:
                criteria['excludeChats'] = exclude_chats
            if size_comparison and size:
                if size_comparison.lower() == 'larger':
                    criteria['sizeComparison'] = 'larger'
                    criteria['size'] = size
                elif size_comparison.lower() == 'smaller':
                    criteria['sizeComparison'] = 'smaller'
                    criteria['size'] = size
            
            action = {}
            if add_label_ids:
                action['addLabelIds'] = add_label_ids
            if remove_label_ids:
                action['removeLabelIds'] = remove_label_ids
            if forward_to:
                action['forward'] = forward_to
            
            filter_object = {
                'criteria': criteria,
                'action': action
            }
            
            created_filter = await asyncio.to_thread(
                self.service.users().settings().filters().create(
                    userId="me", 
                    body=filter_object
                ).execute
            )
            
            logger.info(f"Filter created: {created_filter['id']}")
            return {
                'status': 'success',
                'filter_id': created_filter['id'],
                'filter': created_filter
            }
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}
    
    async def delete_filter(self, filter_id: str) -> str:
        """Deletes a filter by ID"""
        try:
            await asyncio.to_thread(
                self.service.users().settings().filters().delete(
                    userId="me", 
                    id=filter_id
                ).execute
            )
            
            logger.info(f"Filter deleted: {filter_id}")
            return f"Filter deleted successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def search_emails(self, query: str, max_results: int = 50) -> list[dict] | str:
        """Searches for emails using Gmail's search syntax."""
        try:
            user_id = 'me'
            
            response = await asyncio.to_thread(
                self.service.users().messages().list(
                    userId=user_id,
                    q=query,
                    maxResults=max_results
                ).execute
            )
            
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response and len(messages) < max_results:
                page_token = response['nextPageToken']
                response = await asyncio.to_thread(
                    self.service.users().messages().list(
                        userId=user_id, 
                        q=query,
                        pageToken=page_token,
                        maxResults=max_results - len(messages)
                    ).execute
                )
                if 'messages' in response:
                    messages.extend(response['messages'])
            
            result_messages = []
            for msg in messages:
                msg_data = await asyncio.to_thread(
                    self.service.users().messages().get(
                        userId=user_id,
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date']
                    ).execute
                )
                
                headers = msg_data.get('payload', {}).get('headers', [])
                
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
                date = next((header['value'] for header in headers if header['name'].lower() == 'date'), '')
                
                result_messages.append({
                    'id': msg['id'],
                    'threadId': msg['threadId'],
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'snippet': msg_data.get('snippet', '')
                })
                
            return result_messages
            
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def create_folder(self, name: str) -> dict | str:
        """Creates a new folder (implemented as a label with special handling)."""
        try:
            label_object = {
                'name': name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
                'type': 'user'
            }
            
            created_label = await asyncio.to_thread(
                self.service.users().labels().create(userId="me", body=label_object).execute
            )
            
            logger.info(f"Folder created: {created_label['id']}")
            return {
                'status': 'success',
                'folder_id': created_label['id'],
                'name': created_label['name']
            }
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}
    
    async def move_to_folder(self, email_id: str, folder_id: str) -> str:
        """Moves an email to a folder."""
        try:
            await asyncio.to_thread(
                self.service.users().messages().modify(
                    userId="me", 
                    id=email_id, 
                    body={'addLabelIds': [folder_id], 'removeLabelIds': ['INBOX']}
                ).execute
            )
            
            logger.info(f"Email {email_id} moved to folder {folder_id}")
            return f"Email moved to folder successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def list_folders(self) -> list[dict] | str:
        """Lists all user-created labels (folders)."""
        try:
            results = await asyncio.to_thread(
                self.service.users().labels().list(userId="me").execute
            )
            labels = results.get('labels', [])
            
            folders = [
                {
                    'id': label['id'],
                    'name': label['name']
                }
                for label in labels
                if label['type'] == 'user'
            ]
                
            return folders
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def rename_label(self, label_id: str, new_name: str) -> dict | str:
        """Renames an existing label."""
        try:
            label = await asyncio.to_thread(
                self.service.users().labels().get(userId="me", id=label_id).execute
            )
            
            label['name'] = new_name
            
            updated_label = await asyncio.to_thread(
                self.service.users().labels().update(
                    userId="me", 
                    id=label_id, 
                    body=label
                ).execute
            )
            
            logger.info(f"Label renamed: {label_id} to {new_name}")
            return {
                'status': 'success',
                'label_id': updated_label['id'],
                'name': updated_label['name']
            }
        except HttpError as error:
            return {"status": "error", "error_message": str(error)}
    
    async def delete_label(self, label_id: str) -> str:
        """Deletes a label."""
        try:
            await asyncio.to_thread(
                self.service.users().labels().delete(
                    userId="me", 
                    id=label_id
                ).execute
            )
            
            logger.info(f"Label deleted: {label_id}")
            return f"Label deleted successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def archive_email(self, email_id: str) -> str:
        """Archives an email by removing the INBOX label."""
        try:
            await asyncio.to_thread(
                self.service.users().messages().modify(
                    userId="me", 
                    id=email_id, 
                    body={'removeLabelIds': ['INBOX']}
                ).execute
            )
            
            logger.info(f"Email archived: {email_id}")
            return f"Email archived successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}"
    
    async def batch_archive(self, query: str, max_emails: int = 100) -> dict:
        """Archives multiple emails matching a search query."""
        try:
            user_id = 'me'
            
            response = await asyncio.to_thread(
                self.service.users().messages().list(
                    userId=user_id,
                    q=query,
                    maxResults=max_emails
                ).execute
            )
            
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            
            if not messages:
                return {
                    'status': 'success',
                    'archived_count': 0,
                    'message': 'No emails found matching the query.'
                }
            
            archived_count = 0
            for msg in messages:
                try:
                    await asyncio.to_thread(
                        self.service.users().messages().modify(
                            userId="me", 
                            id=msg['id'], 
                            body={'removeLabelIds': ['INBOX']}
                        ).execute
                    )
                    archived_count += 1
                except Exception as e:
                    logger.error(f"Error archiving email {msg['id']}: {str(e)}")
            
            logger.info(f"Batch archived {archived_count} emails")
            return {
                'status': 'success',
                'archived_count': archived_count,
                'total_found': len(messages),
                'message': f"Successfully archived {archived_count} out of {len(messages)} emails."
            }
        except HttpError as error:
            return {
                'status': 'error',
                'error_message': str(error)
            }
    
    async def list_archived(self, max_results: int = 50) -> list[dict] | str:
        """Lists archived emails (emails not in inbox)."""
        try:
            query = "-in:inbox"
            return await self.search_emails(query, max_results)
        except Exception as error:
            return f"An error occurred: {str(error)}"
    
    async def restore_to_inbox(self, email_id: str) -> str:
        """Restores an archived email to the inbox."""
        try:
            await asyncio.to_thread(
                self.service.users().messages().modify(
                    userId="me", 
                    id=email_id, 
                    body={'addLabelIds': ['INBOX']}
                ).execute
            )
            
            logger.info(f"Email restored to inbox: {email_id}")
            return f"Email restored to inbox successfully."
        except HttpError as error:
            return f"An HttpError occurred: {str(error)}" 