"""Agente ejecutor de un solo paso (estilo ReAct)."""
from langchain.agents import initialize_agent, AgentType
from .config import LLM_EXECUTOR
from .prompts import EXECUTOR_PREFIX
from .tools.weather import (
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice
)
# Importar herramientas de Google Tasks
from .tools.tasks import (
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    edit_task,
    search_tasks
)

# Todas las herramientas disponibles
TOOLS = [
    # Herramientas de clima
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice,
    # Herramientas de tareas
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    edit_task,
    search_tasks
]

# Configuración optimizada para permitir múltiples llamadas a herramientas
agent_executor = initialize_agent(
    TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    agent_kwargs={"system_message": EXECUTOR_PREFIX},  # Aplicar el prompt mejorado
    max_iterations=10,  # Permitir más iteraciones para múltiples herramientas
    max_execution_time=60,  # Timeout de 60 segundos
    early_stopping_method="generate",  # Continuar hasta completar la tarea
    handle_parsing_errors=True,  # Manejar errores de parsing
)
