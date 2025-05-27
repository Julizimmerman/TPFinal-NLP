"""Create the high-level plan."""
from .prompts import PLANNER_PROMPT
from .config import LLM_PLANNER
from .schemas import Plan

def make_plan(user_input: str) -> Plan:
    res = PLANNER_PROMPT | LLM_PLANNER
    plan_text = res.invoke({"input": user_input}).content
    steps = [line.split(".", 1)[1].strip() for line in plan_text.splitlines()
             if "." in line]
    return Plan(steps=steps)
