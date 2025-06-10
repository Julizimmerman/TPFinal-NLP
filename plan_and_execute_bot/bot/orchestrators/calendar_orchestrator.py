"""Orquestador especializado para gestión de Google Calendar."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..schemas import PlanExecute
from ..config import LLM_EXECUTOR
from ..tools.calendar import list_calendars, list_events, get_event, create_event, update_event, delete_event, find_free_slot
from ..memory import memory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Herramientas específicas de Calendar
CALENDAR_TOOLS = [
    list_calendars,
    list_events,
    get_event,
    create_event,
    update_event,
    delete_event,
    find_free_slot
]

# Prompt especializado para Calendar
CALENDAR_SPECIALIST_PROMPT = ChatPromptTemplate.from_template("""
Eres un especialista en gestión de calendario y eventos usando Google Calendar.

**Capacidades que tienes:**
- 📅 Crear eventos y reuniones con fecha, hora y detalles
- 📋 Listar eventos programados por fecha o rango
- 🔍 Buscar eventos específicos
- ✏️ Editar eventos existentes
- ❌ Eliminar eventos
- 🆓 Encontrar horarios libres para agendar reuniones
- 📊 Gestionar múltiples calendarios

**PROTOCOLO PARA CREAR EVENTOS:**
Si el usuario quiere crear un evento, necesitas:
1. **Título/Asunto** del evento
2. **Fecha** (hoy, mañana, fecha específica)
3. **Hora** de inicio (y duración si es posible)
4. **Ubicación** (opcional)
5. **Descripción** adicional (opcional)

**Ejemplos de interpretación:**
- "Reunión con cliente mañana a las 3" → Crear evento para mañana 15:00
- "Cita médica el viernes 10:30" → Crear evento viernes próximo 10:30
- "Recordar cumpleaños de María el 15" → Crear evento día 15

**MANEJO DE FECHAS:**
- "Hoy" = fecha actual
- "Mañana" = fecha actual + 1 día  
- "La próxima semana" = semana siguiente
- "El viernes" = próximo viernes

**Contexto de conversación:**
{chat_history}

**Usuario:** {input}

{agent_scratchpad}
""")

async def calendar_orchestrator_node(state: PlanExecute):
    """Orquestador especializado que maneja todas las tareas de Google Calendar."""
    
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"📅 [CALENDAR_ORCHESTRATOR] Procesando: {user_input[:50]}...")
    
    # Crear agente especializado en Calendar
    agent = create_tool_calling_agent(
        llm=LLM_EXECUTOR,
        tools=CALENDAR_TOOLS,
        prompt=CALENDAR_SPECIALIST_PROMPT
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=CALENDAR_TOOLS,
        verbose=True,
        max_iterations=5,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    
    try:
        # Obtener contexto de conversación
        chat_history = "Esta es una nueva conversación."
        if session_id:
            chat_history = memory.get_context_for_planning(session_id, max_messages=5)
        
        # Ejecutar agente Calendar
        result = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        response = result.get("output", "No se pudo procesar la solicitud de Calendar.")
        print(f"📅 [CALENDAR_ORCHESTRATOR] Respuesta: {response[:100]}...")
        
        return {"response": response}
        
    except Exception as e:
        error_msg = f"❌ Error en Calendar: {str(e)}"
        print(f"📅 [CALENDAR_ORCHESTRATOR] {error_msg}")
        return {"response": error_msg} 