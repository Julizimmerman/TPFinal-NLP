"""Create the high-level plan."""
from .prompts import PLANNER_PROMPT
from .config import LLM_PLANNER
from .schemas import Plan
from .memory import memory

async def make_plan(user_input: str, session_id: str = None) -> Plan:
    """Crear un plan considerando el contexto de conversación.
    
    Args:
        user_input: Entrada del usuario
        session_id: ID de la sesión para obtener contexto
        
    Returns:
        Plan con pasos a seguir
    """
    # Obtener contexto de conversación si hay una sesión activa
    context = ""
    if session_id:
        context = memory.get_context_for_planning(session_id)
        print(f"🧠 [PLANNER] Usando contexto de conversación para sesión {session_id[:8]}...")
    
    # Preparar el input con contexto
    input_with_context = user_input
    if context and context != "Esta es una nueva conversación.":
        input_with_context = f"{context}\n\nNueva consulta del usuario: {user_input}"
    
    res = PLANNER_PROMPT | LLM_PLANNER
    plan_text = (await res.ainvoke({"input": input_with_context})).content
    steps = [line.split(".", 1)[1].strip() for line in plan_text.splitlines()
             if "." in line]
    
    print(f"🧠 [PLANNER] Plan generado con {len(steps)} pasos")
    return Plan(steps=steps)
