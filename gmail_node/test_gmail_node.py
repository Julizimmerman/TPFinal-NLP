import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from gmail_node import GmailNode

async def test_gmail_node():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    creds_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    print(f"Azure OpenAI API Key: {azure_openai_api_key}")
    
    # Initialize Gmail node
    print("Initializing Gmail node...")
    gmail_node = GmailNode(
        creds_file_path=creds_file_path,
        token_path=token_path,
        azure_openai_api_key=azure_openai_api_key,
        azure_openai_endpoint="https://zimme-mb6x0rnm-eastus2.cognitiveservices.azure.com/",
        azure_deployment_name="gpt-4o-mini",
        azure_api_version="2025-01-01-preview"
    )
    
    # Test 1: List unread emails
    print("\nTest 1: Listing unread emails...")
    response = await gmail_node.process_request("Show me recent unread emails")
    print(f"Response: {response}")
    
    # Test 2: Search for recent emails
    print("\nTest 2: Searching for recent emails...")
    response = await gmail_node.search_emails("after:2024/01/01")
    print(f"Response: {response}")
    
    # Test 3: List labels
    print("\nTest 3: Listing labels...")
    response = await gmail_node.manage_labels("List all my labels")
    print(f"Response: {response}")
    
    # Test 4: Draft an email
    print("\nTest 4: Drafting an email...")
    response = await gmail_node.draft_email(
        content="Testing the Gmail node functionality",
        recipient="Test User",
        recipient_email="test@example.com"
    )
    print(f"Response: {response}")
    
    # Test 5: List folders
    print("\nTest 5: Listing folders...")
    response = await gmail_node.manage_folders("List all my folders")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_gmail_node()) 