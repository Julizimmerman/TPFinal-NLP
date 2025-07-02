"""Router que decide qué ejecutor especializado usar."""
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from ..config import LLM_PLANNER
from ..memory import memory

ROUTER_PROMPT = PromptTemplate.from_template(
    """Eres un router inteligente que decide qué ejecutor especializado debe manejar una tarea.

TAREA A ROUTEAR: {task}

EXECUTORES DISPONIBLES:
- weather_executor: Para tareas relacionadas con clima, pronósticos, calidad del aire, horarios de sol
- tasks_executor: Para tareas relacionadas con Google Tasks (crear, listar, completar, eliminar, editar, buscar tareas)
- drive_executor: Para tareas relacionadas con Google Drive (buscar, descargar, subir, mover, eliminar archivos)
- gmail_executor: Para tareas relacionadas con Gmail (enviar, recibir, responder, eliminar mensajes, gestionar etiquetas)
- calendar_executor: Para tareas relacionadas con Google Calendar (crear, editar, eliminar eventos)

CONTEXTO DE CONVERSACIÓN:
{conversation_context}

INSTRUCCIONES:
1. Analiza la tarea cuidadosamente
2. Identifica qué tipo de operación se requiere
3. Selecciona el ejecutor más apropiado
4. Responde SOLO con el nombre del ejecutor (ej: "weather_executor")

EJEMPLOS:
- "Obtener el clima en Madrid" → weather_executor
- "Crear una tarea llamada 'Reunión'" → tasks_executor  
- "Buscar archivos en Drive" → drive_executor
- "Enviar un email a Juan" → gmail_executor
- "Crear un evento en el calendario" → calendar_executor

RESPUESTA:"""
)

async def route_task(task: str, session_id: str = None) -> str:
    """
    Rutea una tarea al ejecutor especializado apropiado.
    
    Args:
        task: La tarea a ejecutar
        session_id: ID de la sesión para obtener contexto
        
    Returns:
        str: Nombre del ejecutor especializado
    """
    print(f"🔄 [ROUTER] Iniciando routing para tarea: {task}")
    
    # Obtener contexto de conversación
    conversation_context = "Esta es una nueva conversación."
    if session_id:
        conversation_context = memory.get_context_for_planning(session_id, max_messages=3)
    
    # Crear la cadena de prompt + LLM
    prompt_chain = ROUTER_PROMPT | LLM_PLANNER
    
    try:
        # Obtener decisión del router
        response = await prompt_chain.ainvoke({
            "task": task,
            "conversation_context": conversation_context
        })
        
        executor_name = response.content.strip().lower()
        print(f"🔄 [ROUTER] Tarea '{task}' ruteada a: {executor_name}")
        
        return executor_name
        
    except Exception as e:
        print(f"🔄 [ROUTER] Error en routing: {e}")
        # Fallback: intentar detectar por palabras clave
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["clima", "tiempo", "temperatura", "lluvia", "sol", "aire"]):
            return "weather_executor"
        elif any(word in task_lower for word in ["tarea", "task", "completar", "eliminar tarea"]):
            return "tasks_executor"
        elif any(word in task_lower for word in ["archivo", "drive", "subir", "descargar", "buscar archivo"]):
            return "drive_executor"
        elif any(word in task_lower for word in ["email", "correo", "gmail", "enviar", "mensaje"]):
            return "gmail_executor"
        elif any(word in task_lower for word in ["evento", "calendario", "reunión", "cita"]):
            return "calendar_executor"
        else:
            print(f"🔄 [ROUTER] No se pudo determinar el ejecutor, usando weather_executor como fallback")
            return "weather_executor" 