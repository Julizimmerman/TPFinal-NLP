"""Ejecutor principal que coordina todos los ejecutores especializados."""
from typing import Dict, Any
from .router import route_task
from .weather_executor import execute_weather_task
from .tasks_executor import execute_tasks_task
from .drive_executor import execute_drive_task
from .gmail_executor import execute_gmail_task
from .calendar_executor import execute_calendar_task

# Mapeo de ejecutores especializados
EXECUTOR_MAP = {
    "weather_executor": execute_weather_task,
    "tasks_executor": execute_tasks_task,
    "drive_executor": execute_drive_task,
    "gmail_executor": execute_gmail_task,
    "calendar_executor": execute_calendar_task,
}

async def execute_specialized_task(task: str, session_id: str = None) -> str:
    """
    Ejecuta una tarea usando el ejecutor especializado apropiado.
    
    Args:
        task: La tarea a ejecutar
        session_id: ID de la sesión para contexto
        
    Returns:
        str: Resultado de la ejecución
    """
    print(f"🔄 [SPECIALIZED_EXECUTOR] Iniciando ejecución especializada para: {task}")
    
    try:
        # 1. Router decide qué ejecutor usar
        print(f"🔄 [SPECIALIZED_EXECUTOR] Consultando router...")
        executor_name = await route_task(task, session_id)
        
        # 2. Obtener el ejecutor correspondiente
        if executor_name not in EXECUTOR_MAP:
            print(f"🔄 [SPECIALIZED_EXECUTOR] Ejecutor '{executor_name}' no encontrado, usando weather_executor como fallback")
            executor_name = "weather_executor"
        
        executor_func = EXECUTOR_MAP[executor_name]
        print(f"🔄 [SPECIALIZED_EXECUTOR] Usando ejecutor: {executor_name}")
        
        # 3. Ejecutar la tarea con el ejecutor especializado
        print(f"🔄 [SPECIALIZED_EXECUTOR] Invocando {executor_name}...")
        result = await executor_func(task)
        
        print(f"🔄 [SPECIALIZED_EXECUTOR] Ejecución completada con {executor_name}")
        return result
        
    except Exception as e:
        error_msg = f"Error en specialized_executor: {str(e)}"
        print(f"🔄 [SPECIALIZED_EXECUTOR] {error_msg}")
        return error_msg

async def execute_multiple_tasks(tasks: list, session_id: str = None) -> str:
    """
    Ejecuta múltiples tareas relacionadas usando los ejecutores apropiados.
    
    Args:
        tasks: Lista de tareas a ejecutar
        session_id: ID de la sesión para contexto
        
    Returns:
        str: Resultado combinado de todas las ejecuciones
    """
    print(f"🔄 [SPECIALIZED_EXECUTOR] Ejecutando múltiples tareas: {tasks}")
    
    results = []
    
    for i, task in enumerate(tasks, 1):
        print(f"🔄 [SPECIALIZED_EXECUTOR] Ejecutando tarea {i}/{len(tasks)}: {task}")
        result = await execute_specialized_task(task, session_id)
        results.append(f"Tarea {i}: {result}")
    
    combined_result = "\n\n".join(results)
    print(f"🔄 [SPECIALIZED_EXECUTOR] Todas las tareas completadas")
    return combined_result 