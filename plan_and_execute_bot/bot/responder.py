"""Módulo para generar respuestas finales pulidas usando LLM."""
from typing import List, Tuple, Optional, Union
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from .config import LLM_PLANNER  # Reutilizamos el LLM del planner
from .memory import memory
from .schemas import StepResult
from datetime import datetime, timezone, timedelta
BA = timezone(timedelta(hours=-3))      # tu huso horario
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")


# Prompt para generar respuesta final
RESPONDER_BASE = """
                                                    
*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.
                                                    
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

**REGLAS IMPORTANTES:**
- Si el resultado contiene palabras como "eliminado exitosamente", "creado exitosamente", "actualizado exitosamente", "exitoso", "completado correctamente", entonces la tarea SE COMPLETÓ EXITOSAMENTE
- Si la tarea se completó exitosamente, NO menciones errores o fallos previos
- Si la tarea se completó exitosamente, reporta SOLO el éxito
- Si hay múltiples resultados, prioriza el resultado exitoso sobre los errores

Genera SOLO la respuesta final, sin explicaciones adicionales sobre el proceso.
"""

RESPONDER_PROMPT = (
    PromptTemplate
    .from_template(RESPONDER_BASE)
    .partial(TODAY=TODAY)
)

async def generate_final_response(
    query: str,
    tool_result: str,
    session_id: Optional[str] = None,
    past_steps: Optional[Union[List[Tuple[str, str]], List[StepResult]]] = None
) -> str:
    """
    Genera una respuesta final pulida usando LLM.
    
    Args:
        query: La consulta original del usuario
        tool_result: El resultado obtenido de las herramientas
        session_id: ID de sesión para obtener contexto de conversación
        past_steps: Lista de pasos ejecutados (opcional) - puede ser tuplas o StepResult
    
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
    
    # Procesar el tool_result para detectar éxito y limpiar mensajes de error
    processed_tool_result = tool_result
    
    # Si hay éxito en el resultado, extraer solo la parte exitosa
    if any(success_phrase in tool_result.lower() for success_phrase in [
        "eliminado exitosamente", "creado exitosamente", "actualizado exitosamente",
        "evento eliminado", "evento creado", "evento actualizado",
        "exitoso", "completado correctamente"
    ]):
        # Buscar la línea que contiene el éxito
        lines = tool_result.split('\n')
        success_lines = []
        
        for line in lines:
            if any(success_phrase in line.lower() for success_phrase in [
                "eliminado exitosamente", "creado exitosamente", "actualizado exitosamente",
                "evento eliminado", "evento creado", "evento actualizado",
                "exitoso", "completado correctamente"
            ]):
                success_lines.append(line.strip())
        
        if success_lines:
            # Si encontramos líneas de éxito, usar solo esas
            processed_tool_result = "\n".join(success_lines)
            print(f"🔄 [DEBUG] Procesado tool_result para mostrar solo éxito: {processed_tool_result}")
    
    # Si tenemos past_steps, usar el resultado más relevante
    if past_steps:
        # Unir todos los resultados relevantes en un solo string
        combined_results = []
        
        # Manejar tanto el formato antiguo (tuplas) como el nuevo (StepResult)
        for step_data in past_steps:
            if isinstance(step_data, StepResult):
                # Nuevo formato: StepResult
                if step_data.success and step_data.result and len(step_data.result.strip()) > 10:
                    combined_results.append(step_data.result.strip())
            else:
                # Formato antiguo: tupla (step, result)
                step, result = step_data
                if result and len(result.strip()) > 10:
                    combined_results.append(result.strip())
        
        if combined_results:
            # Procesar también los resultados combinados
            combined_tool_result = "\n".join(combined_results)
            
            # Si hay éxito en los resultados combinados, usar solo esa parte
            if any(success_phrase in combined_tool_result.lower() for success_phrase in [
                "eliminado exitosamente", "creado exitosamente", "actualizado exitosamente",
                "evento eliminado", "evento creado", "evento actualizado",
                "exitoso", "completado correctamente"
            ]):
                lines = combined_tool_result.split('\n')
                success_lines = []
                
                for line in lines:
                    if any(success_phrase in line.lower() for success_phrase in [
                        "eliminado exitosamente", "creado exitosamente", "actualizado exitosamente",
                        "evento eliminado", "evento creado", "evento actualizado",
                        "exitoso", "completado correctamente"
                    ]):
                        success_lines.append(line.strip())
                
                if success_lines:
                    processed_tool_result = "\n".join(success_lines)
    
    print(f"🔄 [DEBUG] Contexto de conversación: {conversation_context}")
    
    try:
        # Crear la cadena de prompt + LLM
        prompt_chain = RESPONDER_PROMPT | LLM_PLANNER
        
        # Generar respuesta
        response = await prompt_chain.ainvoke({
            "query": query,
            "tool_result": processed_tool_result,
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
        # Fallback: usar el tool_result procesado directamente
        fallback_response = processed_tool_result if processed_tool_result else "No se pudo obtener la información solicitada."
        
        if session_id:
            memory.add_message(session_id, "assistant", fallback_response)
        
        return fallback_response

def format_past_steps_summary(past_steps: Union[List[Tuple[str, str]], List[StepResult]]) -> str:
    """
    Formatea los pasos ejecutados en un resumen legible.
    
    Args:
        past_steps: Lista de tuplas (tarea, resultado) o StepResult
    
    Returns:
        str: Resumen formateado de los pasos
    """
    if not past_steps:
        return "No se ejecutaron pasos."
    
    summary_parts = []
    for i, step_data in enumerate(past_steps, 1):
        if isinstance(step_data, StepResult):
            # Nuevo formato: StepResult
            task = step_data.step
            result = step_data.result
            executor = step_data.executor
            success = step_data.success
            
            status = "✅" if success else "❌"
            summary_parts.append(f"Paso {i}: {task} (ejecutor: {executor}) {status}")
        else:
            # Formato antiguo: tupla (step, result)
            task, result = step_data
            summary_parts.append(f"Paso {i}: {task}")
        
        if result:
            # Truncar resultados muy largos
            truncated_result = result[:200] + "..." if len(result) > 200 else result
            summary_parts.append(f"Resultado: {truncated_result}")
        summary_parts.append("")  # Línea en blanco
    
    return "\n".join(summary_parts) 