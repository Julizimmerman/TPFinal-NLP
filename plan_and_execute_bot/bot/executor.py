"""Agente ejecutor que utiliza ejecutores especializados."""
from .executors import execute_specialized_task, execute_multiple_tasks

# Función principal para ejecutar tareas usando ejecutores especializados
async def agent_executor(input_data: dict) -> dict:
    """
    Ejecuta tareas usando el sistema de ejecutores especializados.
    
    Args:
        input_data: Diccionario con la entrada del usuario
        
    Returns:
        dict: Resultado de la ejecución
    """
    task = input_data.get("input", "")
    session_id = input_data.get("session_id")
    
    print(f"🔄 [AGENT_EXECUTOR] Ejecutando tarea: {task}")
    
    try:
        # Usar el ejecutor especializado
        result = await execute_specialized_task(task, session_id)
        
        return {"output": result}
        
    except Exception as e:
        error_msg = f"Error en agent_executor: {str(e)}"
        print(f"🔄 [AGENT_EXECUTOR] {error_msg}")
        return {"output": error_msg}

# Función para ejecutar múltiples tareas relacionadas
async def execute_multiple_tasks_executor(tasks: list, session_id: str = None) -> str:
    """
    Ejecuta múltiples tareas usando ejecutores especializados.
    
    Args:
        tasks: Lista de tareas a ejecutar
        session_id: ID de la sesión para contexto
        
    Returns:
        str: Resultado combinado de todas las ejecuciones
    """
    return await execute_multiple_tasks(tasks, session_id)
