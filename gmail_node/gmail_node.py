import os
import logging
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import AzureChatOpenAI

from gmail_node.gmail_service import GmailService
from gmail_node.tools import create_gmail_tools
from gmail_node.prompts import (
    EMAIL_ADMIN_PROMPTS,
    DRAFT_EMAIL_PROMPT,
    EDIT_DRAFT_PROMPT,
    MANAGE_LABELS_PROMPT,
    MANAGE_FILTERS_PROMPT,
    SEARCH_EMAILS_PROMPT,
    MANAGE_FOLDERS_PROMPT,
    MANAGE_ARCHIVE_PROMPT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GmailNode:
    def __init__(
        self,
        creds_file_path: str,
        token_path: str,
        azure_openai_api_key: Optional[str] = None,
        azure_openai_endpoint: str = "https://zimme-mb6x0rnm-eastus2.cognitiveservices.azure.com/",
        azure_deployment_name: str = "gpt-4o-mini",
        azure_api_version: str = "2025-01-01-preview",
        temperature: float = 0.7
    ):
        """Initialize the Gmail node with necessary credentials and configuration.
        
        Args:
            creds_file_path: Path to the Google API credentials file
            token_path: Path to store/retrieve the OAuth token
            azure_openai_api_key: Azure OpenAI API key (optional if set in environment)
            azure_openai_endpoint: Azure OpenAI endpoint URL
            azure_deployment_name: Azure OpenAI deployment name
            azure_api_version: Azure OpenAI API version
            temperature: Temperature setting for the language model
        """
        self.gmail_service = GmailService(creds_file_path, token_path)
        self.tools = create_gmail_tools(self.gmail_service)
        
        # Get API key from parameter or environment variable
        api_key = azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Azure OpenAI API key must be provided either as a parameter or through AZURE_OPENAI_API_KEY environment variable")
            
        self.llm = AzureChatOpenAI(
            openai_api_version=azure_api_version,
            azure_deployment=azure_deployment_name,
            azure_endpoint=azure_openai_endpoint,
            api_key=api_key,
            temperature=temperature
        )
        
        # Create the agent
        self.agent = self._create_agent()
        
    def _create_agent(self) -> AgentExecutor:
        """Create and configure the LangChain agent with Gmail tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", EMAIL_ADMIN_PROMPTS),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        llm_with_tools = self.llm.bind(
            functions=[convert_to_openai_function(t) for t in self.tools]
        )
        
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def process_request(self, request: str) -> Dict[str, Any]:
        """Process a user request using the Gmail agent.
        
        Args:
            request: The user's request as a string
            
        Returns:
            Dict containing the agent's response and any additional information
        """
        try:
            result = await self.agent.ainvoke({"input": request})
            return {
                "status": "success",
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def draft_email(self, content: str, recipient: str, recipient_email: str) -> Dict[str, Any]:
        """Draft an email using the agent.
        
        Args:
            content: The content/topic of the email
            recipient: Name of the recipient
            recipient_email: Email address of the recipient
            
        Returns:
            Dict containing the draft response
        """
        prompt = DRAFT_EMAIL_PROMPT.format(
            content=content,
            recipient=recipient,
            recipient_email=recipient_email
        )
        return await self.process_request(prompt)
    
    async def edit_draft(self, current_draft: str, changes: str) -> Dict[str, Any]:
        """Edit an existing email draft.
        
        Args:
            current_draft: The current draft content
            changes: Requested changes to the draft
            
        Returns:
            Dict containing the edited draft response
        """
        prompt = EDIT_DRAFT_PROMPT.format(
            current_draft=current_draft,
            changes=changes
        )
        return await self.process_request(prompt)
    
    async def manage_labels(self, action: str) -> Dict[str, Any]:
        """Manage Gmail labels.
        
        Args:
            action: The label management action to perform
            
        Returns:
            Dict containing the label management response
        """
        prompt = MANAGE_LABELS_PROMPT.format(action=action)
        return await self.process_request(prompt)
    
    async def manage_filters(self, action: str) -> Dict[str, Any]:
        """Manage Gmail filters.
        
        Args:
            action: The filter management action to perform
            
        Returns:
            Dict containing the filter management response
        """
        prompt = MANAGE_FILTERS_PROMPT.format(action=action)
        return await self.process_request(prompt)
    
    async def search_emails(self, query: str) -> Dict[str, Any]:
        """Search for emails using Gmail's search syntax.
        
        Args:
            query: The search query
            
        Returns:
            Dict containing the search results
        """
        prompt = SEARCH_EMAILS_PROMPT.format(query=query)
        return await self.process_request(prompt)
    
    async def manage_folders(self, action: str) -> Dict[str, Any]:
        """Manage Gmail folders.
        
        Args:
            action: The folder management action to perform
            
        Returns:
            Dict containing the folder management response
        """
        prompt = MANAGE_FOLDERS_PROMPT.format(action=action)
        return await self.process_request(prompt)
    
    async def manage_archive(self, action: str) -> Dict[str, Any]:
        """Manage archived emails.
        
        Args:
            action: The archive management action to perform
            
        Returns:
            Dict containing the archive management response
        """
        prompt = MANAGE_ARCHIVE_PROMPT.format(action=action)
        return await self.process_request(prompt) 