from langchain.prompts import PromptTemplate

PLANNER_PROMPT = PromptTemplate.from_template(
    """You are the planning module of an AI assistant with conversation memory.
    
Context and user request: {input}

Analyze the input carefully. If it contains conversation history, consider previous context when planning.
If the user refers to previous information (like "that city", "the weather I asked about", etc.), 
use the conversation context to understand what they mean.

Break the request into a concise, ordered list of steps.
Respond ONLY with numbered steps.

Examples:
- If user asks "What's the weather in Madrid?" → "1. Get current weather for Madrid"
- If user then asks "What about tomorrow?" → "1. Get weather forecast for Madrid for tomorrow"
- If user asks "How about Barcelona?" → "1. Get current weather for Barcelona"
"""
)

REPLANNER_PROMPT = PromptTemplate.from_template(
    """You are updating a multi-step plan with conversation awareness.
User request: {input}

Original plan:
{plan}

Steps already finished:
{past_steps}

Consider the conversation context when deciding next steps. If the user is asking follow-up questions
or referring to previous information, make sure the plan addresses their actual intent.

Return EITHER:
1) "RESPONSE: <final answer>" if the task is complete, OR
2) "PLAN: <new numbered plan>" if more steps remain.
Do NOT repeat completed steps.
"""
)

EXECUTOR_PREFIX = """You are the execution agent with conversation awareness.
Carry out the assigned sub-task and answer concisely.
If the task refers to previous conversation context, use that information appropriately."""
