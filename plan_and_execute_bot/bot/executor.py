"""Single-step executor agent (ReAct style)."""
from langchain.agents import initialize_agent, AgentType
from .config import LLM_EXECUTOR
from .tools.weather import (
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice
)

# Todas las herramientas disponibles del módulo weather
TOOLS = [
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice
]

agent_executor = initialize_agent(
    TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    prefix_prompt="",
    suffix_prompt="",
)
