"""Pydantic data shapes shared across the graph."""
from typing import List, Tuple, Union, Dict, Any, Optional
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field
import operator


class ConversationMessage(BaseModel):
    """Mensaje individual en la conversación."""
    role: str = Field(description="Rol del mensaje: 'user' o 'assistant'")
    content: str = Field(description="Contenido del mensaje")
    timestamp: str = Field(description="Timestamp del mensaje")


class PlanExecute(TypedDict, total=False):
    # Core fields
    input: Optional[str]
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: Optional[str]
    
    # Alternative input formats
    messages: Optional[List[Dict[str, Any]]]
    message: Optional[str]
    
    # Memory fields
    conversation_history: Annotated[List[Dict[str, Any]], operator.add]
    session_id: Optional[str]
    
    # Intent classification for routing
    intent: Optional[str]


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )

    
