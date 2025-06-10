"""Orquestador especializado para gestión de Gmail."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from ..schemas import PlanExecute
from ..config import LLM_EXECUTOR
from ..tools.gmail import list_messages, get_message, send_message, reply_message, delete_message, modify_labels
from ..memory import memory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Herramientas específicas de Gmail
GMAIL_TOOLS = [
    list_messages,
    get_message, 
    send_message,
    reply_message,
    delete_message,
    modify_labels
]

# Prompt especializado para Gmail
GMAIL_SPECIALIST_PROMPT = ChatPromptTemplate.from_template("""
Eres un especialista en gestión de Gmail. Tu trabajo es ayudar al usuario con todas sus tareas relacionadas con correo electrónico.

**Capacidades que tienes:**
- 📧 Enviar correos nuevos con destinatarios, asunto y contenido
- 📬 Leer y buscar mensajes en la bandeja de entrada
- ↩️ Responder a mensajes existentes
- 🗑️ Eliminar mensajes 
- 🏷️ Gestionar etiquetas de mensajes
- 📋 Listar mensajes con filtros específicos

**PROTOCOLO IMPORTANTE:**
1. **Para ENVIAR correos**: Si el usuario quiere enviar un correo pero no proporciona:
   - Destinatario(s) (campo 'to')
   - Asunto del mensaje
   - Contenido/cuerpo del mensaje
   
   Entonces DEBES preguntarle por esta información ANTES de intentar enviarlo.

2. **Para LEER mensajes**: Usa la herramienta list_messages con filtros apropiados

3. **Para RESPONDER**: Primero obtén el mensaje original si necesitas más contexto

4. **Confirmación**: Siempre confirma los detalles importantes antes de ejecutar acciones irreversibles

**Ejemplo de flujo para enviar correo:**
- Usuario: "Envía un email"
- Tú: "Por supuesto. Necesito algunos detalles:
  • ¿A quién quieres enviar el correo? (email del destinatario)
  • ¿Cuál será el asunto?
  • ¿Qué mensaje quieres enviar?"

**Contexto de conversación:**
{chat_history}

**Usuario:** {input}

{agent_scratchpad}
""")

async def gmail_orchestrator_node(state: PlanExecute):
    """Orquestador especializado que maneja todas las tareas de Gmail."""
    
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"📧 [GMAIL_ORCHESTRATOR] Procesando: {user_input[:50]}...")
    
    # Crear agente especializado en Gmail
    agent = create_tool_calling_agent(
        llm=LLM_EXECUTOR,
        tools=GMAIL_TOOLS,
        prompt=GMAIL_SPECIALIST_PROMPT
    )
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=GMAIL_TOOLS,
        verbose=True,
        max_iterations=5,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    
    try:
        # Obtener contexto de conversación específico para Gmail
        chat_history = "Esta es una nueva conversación."
        if session_id:
            chat_history = memory.get_context_for_planning(session_id, max_messages=5)
        
        # Ejecutar agente Gmail
        result = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        response = result.get("output", "No se pudo procesar la solicitud de Gmail.")
        print(f"📧 [GMAIL_ORCHESTRATOR] Respuesta: {response[:100]}...")
        
        return {"response": response}
        
    except Exception as e:
        error_msg = f"❌ Error en Gmail: {str(e)}"
        print(f"📧 [GMAIL_ORCHESTRATOR] {error_msg}")
        return {"response": error_msg} 