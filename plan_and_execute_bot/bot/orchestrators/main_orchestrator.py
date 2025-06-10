"""Orquestador principal que entiende la intención y rutea a especialistas."""
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from ..schemas import PlanExecute
from ..config import LLM_PLANNER
from ..memory import memory
from langchain.prompts import ChatPromptTemplate

# Prompt para clasificar la intención del usuario
INTENT_CLASSIFIER_PROMPT = ChatPromptTemplate.from_template("""
Eres un clasificador de intenciones para un asistente virtual.

Tu tarea es analizar la consulta del usuario y determinar a qué servicio específico debe dirigirse.

Servicios disponibles:
- GMAIL: Para enviar correos, leer emails, responder mensajes, gestionar bandeja de entrada
- CALENDAR: Para crear eventos, agendar reuniones, consultar calendario, gestionar citas
- TASKS: Para crear tareas, gestionar listas de pendientes, marcar como completadas
- DRIVE: Para buscar archivos, subir documentos, gestionar carpetas, compartir archivos
- WEATHER: Para consultar clima, pronósticos, información meteorológica
- GENERAL: Para conversación general, preguntas que no requieren servicios específicos

Consulta del usuario: {input}

Contexto de conversación (si existe):
{context}

IMPORTANTE: Analiza cuidadosamente la intención. Algunos ejemplos:

GMAIL:
- "Envía un email a juan@email.com"
- "Revisa mi bandeja de entrada"
- "Responde al último correo"
- "Elimina el correo de spam"

CALENDAR:
- "Crea una reunión para mañana"
- "¿Qué tengo programado hoy?"
- "Agenda una cita con el doctor"
- "Busca un horario libre"

TASKS:
- "Agrega comprar leche a mi lista"
- "Marca como completada la tarea de estudiar"
- "¿Cuáles son mis tareas pendientes?"
- "Elimina la tarea de limpiar"

DRIVE:
- "Busca el documento de presupuesto"
- "Sube este archivo a Drive"
- "Comparte la carpeta con mi equipo"
- "¿Dónde está mi presentación?"

WEATHER:
- "¿Cómo está el clima?"
- "¿Va a llover mañana?"
- "Pronóstico para la semana"
- "¿Qué ropa debo usar hoy?"

GENERAL:
- "Hola, ¿cómo estás?"
- "¿Qué puedes hacer?"
- "Explícame cómo funciona esto"
- "Gracias por tu ayuda"

Responde ÚNICAMENTE con el nombre del servicio (GMAIL, CALENDAR, TASKS, DRIVE, WEATHER, o GENERAL).
Si no estás seguro, responde GENERAL.

SERVICIO:
""")

async def main_orchestrator_node(state: PlanExecute):
    """Nodo principal que clasifica y prepara el estado para el orquestador especializado."""
    
    # Preservar input del usuario de manera robusta
    user_input = state.get("input", "")
    if not user_input and "messages" in state and state["messages"]:
        last_message = state["messages"][-1]
        if isinstance(last_message, dict):
            user_input = last_message.get("content", "")
        else:
            user_input = str(last_message)
    elif not user_input:
        user_input = state.get("message", "")
    
    if not user_input:
        print("❌ [MAIN_ORCHESTRATOR] No se pudo obtener input del usuario")
        return {
            **state,
            "intent": "GENERAL",
            "input": user_input
        }
    
    # Obtener contexto de conversación
    session_id = state.get("session_id")
    context = "Esta es una nueva conversación."
    if session_id:
        context = memory.get_context_for_planning(session_id, max_messages=3)
    
    # Clasificar intención
    try:
        prompt_chain = INTENT_CLASSIFIER_PROMPT | LLM_PLANNER
        response = await prompt_chain.ainvoke({
            "input": user_input,
            "context": context
        })
        
        intent = response.content.strip().upper()
        
        # Validar que sea un servicio válido
        valid_services = ["GMAIL", "CALENDAR", "TASKS", "DRIVE", "WEATHER", "GENERAL"]
        if intent not in valid_services:
            print(f"⚠️ [MAIN_ORCHESTRATOR] Intent inválido '{intent}', usando GENERAL")
            intent = "GENERAL"
            
        print(f"🎯 [MAIN_ORCHESTRATOR] Usuario: '{user_input[:50]}...' → Servicio: {intent}")
        
        # Preparar estado con intent claramente definido
        result = {
            **state,
            "input": user_input,
            "intent": intent,
            "conversation_history": state.get("conversation_history", [])
        }
        
        print(f"🎭 [MAIN_ORCHESTRATOR] Estado preparado con intent: {intent}")
        return result
        
    except Exception as e:
        print(f"❌ [MAIN_ORCHESTRATOR] Error clasificando intención: {e}")
        return {
            **state,
            "input": user_input,
            "intent": "GENERAL",
            "conversation_history": state.get("conversation_history", [])
        }

def route_to_specialist(state: PlanExecute) -> str:
    """Función de routing que decide a qué orquestador especializado dirigir."""
    intent = state.get("intent", "GENERAL")
    
    print(f"🔍 [ROUTER] Estado recibido - keys: {list(state.keys())}")
    print(f"🔍 [ROUTER] Intent detectado: '{intent}'")
    
    routing_map = {
        "GMAIL": "gmail_orchestrator",
        "CALENDAR": "calendar_orchestrator", 
        "TASKS": "tasks_orchestrator",
        "DRIVE": "drive_orchestrator",
        "WEATHER": "weather_orchestrator",
        "GENERAL": "general_response"
    }
    
    destination = routing_map.get(intent, "general_response")
    print(f"🎯 [ROUTER] Redirigiendo '{intent}' hacia: {destination}")
    return destination

async def general_response_node(state: PlanExecute):
    """Nodo para respuestas generales que no requieren servicios específicos."""
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"💬 [GENERAL] Procesando respuesta general para: {user_input[:50]}...")
    
    general_prompt = ChatPromptTemplate.from_template("""
Eres un asistente virtual amigable y profesional. Tu nombre es "Asistente Virtual".

Responde de manera conversacional, útil y personalizada al usuario.

Si el usuario pregunta por tus funcionalidades, explica que puedes ayudar con:
- 📧 **Gmail**: Enviar correos, leer mensajes, gestionar bandeja de entrada
- 📅 **Calendar**: Crear eventos, agendar reuniones, consultar calendario
- 📋 **Tasks**: Crear y gestionar tareas, listas de pendientes
- 📁 **Drive**: Buscar archivos, gestionar documentos y carpetas
- 🌤️ **Weather**: Consultar clima, pronósticos meteorológicos

Contexto de conversación previo:
{context}

Usuario: {input}

Responde de manera natural y útil:
""")
    
    try:
        # Obtener contexto de conversación
        context = "Esta es una nueva conversación."
        if session_id:
            context = memory.get_context_for_planning(session_id, max_messages=5)
        
        prompt_chain = general_prompt | LLM_PLANNER
        response = await prompt_chain.ainvoke({
            "input": user_input,
            "context": context
        })
        
        result = {"response": response.content}
        print(f"💬 [GENERAL] Respuesta generada: {response.content[:100]}...")
        return result
        
    except Exception as e:
        print(f"❌ [GENERAL] Error: {e}")
        return {"response": "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy? 😊"} 