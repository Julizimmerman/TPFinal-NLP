EMAIL_ADMIN_PROMPTS = """You are an email administrator. 
You can draft, edit, read, trash, open, and send emails.
You've been given access to a specific gmail account. 
You have the following tools available:
- Send an email (send-email)
- Create a draft email (create-draft)
- List draft emails (list-drafts)
- Retrieve unread emails (get-unread-emails)
- Read email content (read-email)
- Trash email (trash-email)
- Open email in browser (open-email)
- List all labels (list-labels)
- Create a new label (create-label)
- Apply a label to an email (apply-label)
- Remove a label from an email (remove-label)
- Rename a label (rename-label)
- Delete a label (delete-label)
- Search for emails with a specific label (search-by-label)
- Search for emails using Gmail's search syntax (search-emails)
- List all email filters (list-filters)
- Get details of a specific filter (get-filter)
- Create a new email filter (create-filter)
- Delete a filter (delete-filter)
- Create a new folder (create-folder)
- Move an email to a folder (move-to-folder)
- List all folders (list-folders)
- Archive an email (archive-email)
- Batch archive emails (batch-archive)
- List archived emails (list-archived)
- Restore an email to inbox (restore-to-inbox)

Never send an email draft or trash an email unless the user confirms first. 
Always ask for approval if not already given.

When showing unread emails, always display ALL unread emails in the response, not just a subset.
Format each email with its subject, sender, and date.
"""

DRAFT_EMAIL_PROMPT = """Please draft an email about {content} for {recipient} ({recipient_email}).
Include a subject line starting with 'Subject:' on the first line.
Do not send the email yet, just draft it and ask the user for their thoughts."""

EDIT_DRAFT_PROMPT = """Please revise the current email draft:
{current_draft}

Requested changes:
{changes}

Please provide the updated draft."""

MANAGE_LABELS_PROMPT = """I need help with managing my email labels. Specifically, I want to {action}.

Here are the tools you can use for label management:
- list-labels: Lists all existing labels in my Gmail account
- create-label: Creates a new label with a specified name
- apply-label: Applies a label to a specific email
- remove-label: Removes a label from a specific email
- rename-label: Renames an existing label
- delete-label: Permanently deletes a label
- search-by-label: Finds all emails with a specific label

Please help me {action} by using the appropriate tools. If you need to list labels first to get label IDs, please do so."""

MANAGE_FILTERS_PROMPT = """I need help with managing my email filters. Specifically, I want to {action}.

Here are the tools you can use for filter management:
- list-filters: Lists all existing filters in my Gmail account
- get-filter: Gets details of a specific filter
- create-filter: Creates a new filter
- delete-filter: Deletes a specific filter

Please help me {action} by using the appropriate tools. If you need to list filters first to get filter IDs, please do so."""

SEARCH_EMAILS_PROMPT = """I need to search through my emails for: {query}

Here are the tools you can use for searching emails:
- search-emails: Searches all emails using Gmail's search syntax
- get-unread-emails: Gets only unread emails from the inbox

Please help me find emails matching my search criteria. You can use Gmail's search syntax for advanced searches:
- from:sender - Emails from a specific sender
- to:recipient - Emails to a specific recipient
- subject:text - Emails with specific text in the subject
- has:attachment - Emails with attachments
- after:YYYY/MM/DD - Emails after a specific date
- before:YYYY/MM/DD - Emails before a specific date
- is:important - Important emails
- label:name - Emails with a specific label

Please search for emails matching: {query}"""

MANAGE_FOLDERS_PROMPT = """I need help with managing my email folders. Specifically, I want to {action}.

Here are the tools you can use for folder management:
- list-folders: Lists all existing folders in my Gmail account
- create-folder: Creates a new folder with a specified name
- move-to-folder: Moves an email to a specific folder (removes it from inbox)

Please help me {action} by using the appropriate tools. If you need to list folders first to get folder IDs, please do so.

Note: In Gmail, folders are implemented as labels with special handling. When you move an email to a folder, it applies the folder's label and removes the email from the inbox."""

MANAGE_ARCHIVE_PROMPT = """I need help with managing my email archives. Specifically, I want to {action}.

Here are the tools you can use for archive management:
- archive-email: Archives a single email (removes from inbox without deleting)
- batch-archive: Archives multiple emails matching a search query
- list-archived: Lists emails that have been archived
- restore-to-inbox: Restores an archived email back to the inbox

Please help me {action} by using the appropriate tools.

For batch archiving, you can use Gmail's search syntax to find emails to archive:
- from:sender - Emails from a specific sender
- older_than:30d - Emails older than 30 days
- has:attachment - Emails with attachments
- subject:text - Emails with specific text in the subject
- before:YYYY/MM/DD - Emails before a specific date

Note: Archiving in Gmail means removing the email from your inbox while keeping it accessible in "All Mail". It's a great way to declutter your inbox without losing any emails.""" 