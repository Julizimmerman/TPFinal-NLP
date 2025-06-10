"""Orquestador especializado para información meteorológica."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..schemas import PlanExecute
from ..config import LLM_EXECUTOR
from ..tools.weather import get_weather, geocode, get_weekly_summary
from ..memory import memory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Herramientas específicas de Weather
WEATHER_TOOLS = [
    get_weather,
    geocode,
    get_weekly_summary
]

# Prompt especializado para Weather
WEATHER_SPECIALIST_PROMPT = ChatPromptTemplate.from_template("""
Eres un especialista en información meteorológica y pronósticos del tiempo.

**Capacidades que tienes:**
- 🌤️ Consultar clima actual de cualquier ubicación
- 📍 Obtener coordenadas geográficas de ciudades
- 📊 Proporcionar resúmenes semanales del tiempo
- 🌡️ Información detallada de temperatura, humedad, viento
- 🌧️ Pronósticos de lluvia y condiciones climáticas

**PROTOCOLO DE CONSULTA:**
1. **Ubicación**: Si el usuario no especifica ubicación, pregunta por ella
2. **Tipo de consulta**: Determina si quiere clima actual, pronóstico o resumen semanal
3. **Detalles útiles**: Proporciona información práctica como consejos de vestimenta

**Ejemplos de interpretación:**
- "¿Cómo está el clima?" → Preguntar por ubicación
- "Clima en Madrid" → Consultar clima actual de Madrid
- "¿Va a llover mañana en Barcelona?" → Pronóstico para Barcelona
- "Pronóstico de la semana en París" → Resumen semanal París

**RESPUESTAS ÚTILES:**
- Incluye temperatura, condiciones, viento, humedad
- Da consejos prácticos ("lleva paraguas", "usa abrigo")
- Usa emojis para hacer la información más visual

**Contexto de conversación:**
{chat_history}

**Usuario:** {input}

{agent_scratchpad}
""")


async def weather_orchestrator_node(state: PlanExecute):
    """Orquestador especializado que maneja todas las consultas meteorológicas."""
    
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"🌤️ [WEATHER_ORCHESTRATOR] Procesando: {user_input[:50]}...")
    
    # Crear agente especializado en Weather
    agent = create_tool_calling_agent(
        llm=LLM_EXECUTOR,
        tools=WEATHER_TOOLS,
        prompt=WEATHER_SPECIALIST_PROMPT
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=WEATHER_TOOLS,
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    
    try:
        # Obtener contexto de conversación
        chat_history = "Esta es una nueva conversación."
        if session_id:
            chat_history = memory.get_context_for_planning(session_id, max_messages=5)
        
        # Ejecutar agente Weather
        result = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        response = result.get("output", "No se pudo obtener información meteorológica.")
        print(f"🌤️ [WEATHER_ORCHESTRATOR] Respuesta: {response[:100]}...")
        
        return {"response": response}
        
    except Exception as e:
        error_msg = f"❌ Error en Weather: {str(e)}"
        print(f"🌤️ [WEATHER_ORCHESTRATOR] {error_msg}")
        return {"response": error_msg} 