"""Ejecutor especializado para tareas relacionadas con Google Tasks."""
from langchain.agents import initialize_agent, AgentType
from datetime import datetime, timezone, timedelta
from ..config import LLM_EXECUTOR
from ..tools.tasks import (
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    edit_task,
    search_tasks,
    add_subtask
)

# Configuración de fecha actual
BA = timezone(timedelta(hours=-3))  # Huso horario de Argentina
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")

# Herramientas específicas para Google Tasks
TASKS_TOOLS = [
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    edit_task,
    search_tasks,
    add_subtask
]

# Prompt especializado para Google Tasks
TASKS_EXECUTOR_PREFIX = f"""Eres un agente especializado en gestión de tareas con Google Tasks con acceso a herramientas específicas.

*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.

HERRAMIENTAS DISPONIBLES Y CÓMO USARLAS:

1. **create_task(title, description=None, due_date=None)**: Crea una nueva tarea
   - Parámetros: 
     - title (string, obligatorio) - título de la tarea
     - description (string, opcional) - descripción detallada
     - due_date (string, opcional) - fecha límite en formato "YYYY-MM-DD"
   - Ejemplo: create_task("Estudiar para el examen", "Repasar capítulos 1-5", "2024-12-20")
   - Retorna: confirmación de creación con ID de tarea

2. **list_tasks(show_completed=False, max_results=10)**: Lista tareas existentes
   - Parámetros:
     - show_completed (boolean, opcional) - incluir tareas completadas
     - max_results (integer, opcional) - número máximo de resultados
   - Ejemplo: list_tasks(show_completed=False, max_results=5)
   - Retorna: lista de tareas con título, estado, fecha límite

3. **complete_task(task_id)**: Marca una tarea como completada
   - Parámetro: task_id (string, obligatorio) - ID de la tarea
   - Ejemplo: complete_task("abc123")
   - Retorna: confirmación de completado

4. **delete_task(task_id)**: Elimina una tarea
   - Parámetro: task_id (string, obligatorio) - ID de la tarea
   - Ejemplo: delete_task("abc123")
   - Retorna: confirmación de eliminación

5. **edit_task(task_id, title=None, description=None, due_date=None)**: Edita una tarea existente
   - Parámetros:
     - task_id (string, obligatorio) - ID de la tarea
     - title (string, opcional) - nuevo título
     - description (string, opcional) - nueva descripción
     - due_date (string, opcional) - nueva fecha límite
   - Ejemplo: edit_task("abc123", title="Nuevo título", due_date="2024-12-25")
   - Retorna: confirmación de edición

6. **search_tasks(query, max_results=10)**: Busca tareas por palabras clave
   - Parámetros:
     - query (string, obligatorio) - término de búsqueda
     - max_results (integer, opcional) - número máximo de resultados
   - Ejemplo: search_tasks("examen", max_results=5)
   - Retorna: tareas que coinciden con la búsqueda

7. **add_subtask(parent_task_id, title, description=None)**: Agrega una subtarea
   - Parámetros:
     - parent_task_id (string, obligatorio) - ID de la tarea padre
     - title (string, obligatorio) - título de la subtarea
     - description (string, opcional) - descripción de la subtarea
   - Ejemplo: add_subtask("abc123", "Comprar materiales", "Papel, lápices, cuaderno")
   - Retorna: confirmación de creación de subtarea

INSTRUCCIONES DE EJECUCIÓN:
- SIEMPRE especifica qué herramienta vas a usar antes de usarla
- Para listar tareas, primero usa list_tasks para ver qué tareas existen
- Para editar/eliminar tareas, necesitas el task_id (obténlo con list_tasks o search_tasks)
- Si una herramienta falla, explica exactamente por qué
- Proporciona respuestas estructuradas y claras
- Incluye IDs de tareas en las respuestas cuando sea relevante
- IMPORTANTE: Si ves add_subtask en el paso, úsalo exactamente como está especificado. NO lo conviertas en create_task.

FORMATO DE RESPUESTA:
1. "Voy a usar [HERRAMIENTA] para [PROPÓSITO]"
2. "Resultado: [DESCRIPCIÓN CLARA DEL RESULTADO]"
3. "Estado: [EXITOSO/FRACASO] - [EXPLICACIÓN]"
"""

# Configurar el agente especializado
tasks_executor = initialize_agent(
    TASKS_TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    agent_kwargs={"system_message": TASKS_EXECUTOR_PREFIX},
    max_iterations=5,
    max_execution_time=30,
    early_stopping_method="generate",
    handle_parsing_errors=True,
)

async def execute_tasks_task(task: str) -> str:
    """
    Ejecuta una tarea relacionada con Google Tasks.
    
    Args:
        task: La tarea a ejecutar
        
    Returns:
        str: Resultado de la ejecución
    """
    print(f"📋 [TASKS_EXECUTOR] Ejecutando tarea: {task}")
    
    try:
        response = await tasks_executor.ainvoke({"input": task})
        result = response["output"]
        print(f"📋 [TASKS_EXECUTOR] Resultado: {result}")
        return result
    except Exception as e:
        error_msg = f"Error en tasks_executor: {str(e)}"
        print(f"📋 [TASKS_EXECUTOR] {error_msg}")
        return error_msg 