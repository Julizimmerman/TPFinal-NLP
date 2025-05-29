"""Módulo para generar respuestas finales pulidas usando LLM."""
from typing import List, Tuple, Optional
from langchain.prompts import ChatPromptTemplate
from .config import LLM_PLANNER  # Reutilizamos el LLM del planner
from .memory import memory

# Prompt para generar respuesta final
RESPONDER_PROMPT = ChatPromptTemplate.from_template("""
Eres un asistente útil que debe generar una respuesta final clara y bien estructurada.

Tienes la siguiente información:
- Consulta original del usuario: {query}
- Resultado de las herramientas ejecutadas: {tool_result}
- Contexto de conversación reciente: {conversation_context}

Tu tarea es generar una respuesta que:
1. Sea clara y directa
2. Responda específicamente a la consulta del usuario
3. Use la información obtenida de las herramientas
4. Mantenga un tono natural y conversacional
5. Si es información sobre clima, incluya detalles relevantes como temperatura, condiciones, etc.
6. Si no se pudo obtener la información, explica claramente por qué

Genera SOLO la respuesta final, sin explicaciones adicionales sobre el proceso.
""")

async def generate_final_response(
    query: str,
    tool_result: str,
    session_id: Optional[str] = None,
    past_steps: Optional[List[Tuple[str, str]]] = None
) -> str:
    """
    Genera una respuesta final pulida usando LLM.
    
    Args:
        query: La consulta original del usuario
        tool_result: El resultado obtenido de las herramientas
        session_id: ID de sesión para obtener contexto de conversación
        past_steps: Lista de pasos ejecutados (opcional)
    
    Returns:
        str: Respuesta final generada por el LLM
    """
    print("🔄 [DEBUG] Iniciando generate_final_response...")
    print(f"🔄 [DEBUG] Query: {query}")
    print(f"🔄 [DEBUG] Tool result: {tool_result}")
    
    # Obtener contexto de conversación
    conversation_context = "Esta es una nueva conversación."
    if session_id:
        conversation_context = memory.get_context_for_planning(session_id, max_messages=5)
    
    # Si tenemos past_steps, usar el resultado más relevante
    if past_steps:
        # Tomar el último resultado que parezca más completo
        for step, result in reversed(past_steps):
            if result and len(result.strip()) > 10:  # Resultado no vacío y con contenido
                tool_result = result
                break
    
    print(f"🔄 [DEBUG] Contexto de conversación: {conversation_context}")
    
    try:
        # Crear la cadena de prompt + LLM
        prompt_chain = RESPONDER_PROMPT | LLM_PLANNER
        
        # Generar respuesta
        response = await prompt_chain.ainvoke({
            "query": query,
            "tool_result": tool_result,
            "conversation_context": conversation_context
        })
        
        final_response = response.content.strip()
        print(f"🔄 [DEBUG] Respuesta final generada: {final_response}")
        
        # Guardar la respuesta en memoria si hay sesión activa
        if session_id:
            memory.add_message(session_id, "assistant", final_response)
        
        return final_response
        
    except Exception as e:
        print(f"🔄 [DEBUG] Error generando respuesta final: {e}")
        # Fallback: usar el tool_result directamente
        fallback_response = tool_result if tool_result else "No se pudo obtener la información solicitada."
        
        if session_id:
            memory.add_message(session_id, "assistant", fallback_response)
        
        return fallback_response

def format_past_steps_summary(past_steps: List[Tuple[str, str]]) -> str:
    """
    Formatea los pasos ejecutados en un resumen legible.
    
    Args:
        past_steps: Lista de tuplas (tarea, resultado)
    
    Returns:
        str: Resumen formateado de los pasos
    """
    if not past_steps:
        return "No se ejecutaron pasos."
    
    summary_parts = []
    for i, (task, result) in enumerate(past_steps, 1):
        summary_parts.append(f"Paso {i}: {task}")
        if result:
            # Truncar resultados muy largos
            truncated_result = result[:200] + "..." if len(result) > 200 else result
            summary_parts.append(f"Resultado: {truncated_result}")
        summary_parts.append("")  # Línea en blanco
    
    return "\n".join(summary_parts) 