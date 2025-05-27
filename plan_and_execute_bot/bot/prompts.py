from langchain.prompts import PromptTemplate

PLANNER_PROMPT = PromptTemplate.from_template(
    """You are the planning module of an AI assistant.
User request: {input}
Break the request into a concise, ordered list of steps.
Respond ONLY with numbered steps."""
)

REPLANNER_PROMPT = PromptTemplate.from_template(
    """You are updating a multi-step plan.
User request: {input}

Original plan:
{plan}

Steps already finished:
{past_steps}

Return EITHER:
1) "RESPONSE: <final answer>" if the task is complete, OR
2) "PLAN: <new numbered plan>" if more steps remain.
Do NOT repeat completed steps.
"""
)

EXECUTOR_PREFIX = """You are the execution agent.
Carry out the assigned sub-task and answer concisely."""
