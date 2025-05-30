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
# Importar herramientas de Google Drive (nuevas)
from .tools.drive import (
    search_files,
    get_file_metadata,
    download_file,
    upload_file,
    move_file,
    delete_file
)
# Importar herramientas de Gmail (nuevas)
from .tools.gmail import (
    list_messages,
    get_message,
    send_message,
    reply_message,
    delete_message,
    modify_labels
)
# Importar herramientas de Google Calendar
from .tools.calendar import (
    list_calendars,
    list_events,
    get_event,
    create_event,
    update_event,
    delete_event,
    find_free_slot
)

# Todas las herramientas disponibles
TOOLS = [
    # Herramientas de clima
    get_weather,
    geocode,
    get_weekly_summary,
    # Herramientas de tareas
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    edit_task,
    search_tasks,
    # Herramientas de Google Drive (6 nuevas herramientas)
    search_files,
    get_file_metadata,
    download_file,
    upload_file,
    move_file,
    delete_file,
    # Herramientas de Gmail (6 nuevas herramientas)
    list_messages,
    get_message,
    send_message,
    reply_message,
    delete_message,
    modify_labels,
    # Herramientas de Google Calendar (7 herramientas)
    list_calendars,
    list_events,
    get_event,
    create_event,
    update_event,
    delete_event,
    find_free_slot
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
