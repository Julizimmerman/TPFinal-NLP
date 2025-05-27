"""Single-step executor agent (ReAct style)."""
from langchain.agents import initialize_agent, AgentType
from .config import LLM_EXECUTOR
from .tools import get_weather

# Only get_weather for this implementation
TOOLS = [get_weather]

agent_executor = initialize_agent(
    TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    prefix_prompt="",
    suffix_prompt="",
)
