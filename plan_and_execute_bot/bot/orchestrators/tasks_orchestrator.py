"""Orquestador especializado para gestión de Google Tasks."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END  
from ..schemas import PlanExecute
from ..config import LLM_EXECUTOR
from ..tools.tasks import create_task, list_tasks, complete_task, delete_task, edit_task, search_tasks
from ..memory import memory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Herramientas específicas de Tasks
TASKS_TOOLS = [
    create_task,
    list_tasks,
    complete_task, 
    delete_task,
    edit_task,
    search_tasks
]

# Prompt especializado para Tasks
TASKS_SPECIALIST_PROMPT = ChatPromptTemplate.from_template("""
Eres un especialista en gestión de tareas y productividad usando Google Tasks.

**Capacidades que tienes:**
- ✅ Crear nuevas tareas con títulos descriptivos
- 📋 Listar todas las tareas pendientes
- ✔️ Marcar tareas como completadas
- ❌ Eliminar tareas que ya no son necesarias
- ✏️ Editar títulos y notas de tareas existentes
- 🔍 Buscar tareas específicas por palabras clave

**PROTOCOLO DE TRABAJO:**
1. **Crear tareas**: Interpreta frases como "agrega X a mi lista", "recordar hacer Y", "tengo que Z" como solicitudes de crear tareas
2. **Títulos claros**: Asegúrate de que los títulos de las tareas sean descriptivos y útiles
3. **Búsqueda inteligente**: Si el usuario quiere completar/eliminar una tarea pero no la especifica exactamente, ayúdale a encontrarla
4. **Confirmación**: Confirma las acciones importantes como completar o eliminar tareas

**Ejemplos de interpretación:**
- "Agrega comprar leche" → Crear tarea "Comprar leche"
- "Recordar llamar al doctor" → Crear tarea "Llamar al doctor"
- "Terminar el informe" → Crear tarea "Terminar el informe"
- "Ya compré la leche" → Completar tarea relacionada con leche

**Contexto de conversación:**
{chat_history}

**Usuario:** {input}

{agent_scratchpad}
""")

async def tasks_orchestrator_node(state: PlanExecute):
    """Orquestador especializado que maneja todas las tareas de Google Tasks."""
    
    user_input = state.get("input", "")
    session_id = state.get("session_id")
    
    print(f"📋 [TASKS_ORCHESTRATOR] Procesando: {user_input[:50]}...")
    
    # Crear agente especializado en Tasks
    agent = create_tool_calling_agent(
        llm=LLM_EXECUTOR,
        tools=TASKS_TOOLS,
        prompt=TASKS_SPECIALIST_PROMPT
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=TASKS_TOOLS, 
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
        
        # Ejecutar agente Tasks
        result = await agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        response = result.get("output", "No se pudo procesar la solicitud de Tasks.")
        print(f"📋 [TASKS_ORCHESTRATOR] Respuesta: {response[:100]}...")
        
        return {"response": response}
        
    except Exception as e:
        error_msg = f"❌ Error en Tasks: {str(e)}"
        print(f"📋 [TASKS_ORCHESTRATOR] {error_msg}")
        return {"response": error_msg} 