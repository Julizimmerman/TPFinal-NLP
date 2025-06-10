"""Orquestador especializado para gestión de Google Drive."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..schemas import PlanExecute
from ..config import LLM_EXECUTOR
from ..tools.drive import search_files, get_file_metadata, download_file, upload_file, move_file, delete_file
from ..memory import memory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Herramientas específicas de Drive
DRIVE_TOOLS = [
    search_files,
    get_file_metadata,
    download_file,
    upload_file,
    move_file,
    delete_file
]

# Prompt especializado para Drive
DRIVE_SPECIALIST_PROMPT = ChatPromptTemplate.from_template("""
Eres un especialista en gestión de archivos y documentos usando Google Drive.

**Capacidades que tienes:**
- 🔍 Buscar archivos por nombre, tipo o contenido
- 📁 Obtener información detallada de archivos
- ⬇️ Descargar archivos desde Drive
- ⬆️ Subir archivos a Drive
- 📂 Mover archivos entre carpetas
- 🗑️ Eliminar archivos y carpetas

**PROTOCOLO DE BÚSQUEDA:**
- Usa términos específicos para buscar archivos
- Si el usuario menciona "documento", "presentación", "hoja de cálculo", incluye esos términos
- Para archivos recientes, usa filtros de fecha
- Para archivos compartidos, especifica el tipo de búsqueda

**Ejemplos de interpretación:**
- "Busca mi presentación sobre ventas" → Buscar archivos con "presentación" y "ventas"
- "¿Dónde está el presupuesto?" → Buscar archivos con "presupuesto"
- "Archivos de este mes" → Buscar con filtro de fecha actual

**IMPORTANTE:**
- Siempre confirma antes de eliminar archivos
- Proporciona detalles útiles sobre los archivos encontrados
- Si hay múltiples resultados, ayuda al usuario a identificar el correcto

**Contexto de conversación:**
{chat_history}

**Usuario:** {input}

{agent_scratchpad}
""")

async def drive_orchestrator_node(state: PlanExecute):
    """Orquestador especializado que maneja todas las tareas de Google Drive."""
    
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"📁 [DRIVE_ORCHESTRATOR] Procesando: {user_input[:50]}...")
    
    # Crear agente especializado en Drive
    agent = create_tool_calling_agent(
        llm=LLM_EXECUTOR,
        tools=DRIVE_TOOLS,
        prompt=DRIVE_SPECIALIST_PROMPT
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=DRIVE_TOOLS,
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
        
        # Ejecutar agente Drive
        result = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        response = result.get("output", "No se pudo procesar la solicitud de Drive.")
        print(f"📁 [DRIVE_ORCHESTRATOR] Respuesta: {response[:100]}...")
        
        return {"response": response}
        
    except Exception as e:
        error_msg = f"❌ Error en Drive: {str(e)}"
        print(f"📁 [DRIVE_ORCHESTRATOR] {error_msg}")
        return {"response": error_msg} 