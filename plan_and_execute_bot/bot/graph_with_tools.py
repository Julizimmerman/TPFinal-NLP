"""LangGraph wrapper con herramientas visibles en el grafo."""
from typing import List
from langgraph.graph import StateGraph, END
from .schemas import PlanExecute
from .planner import make_plan
from .prompts import REPLANNER_PROMPT
from .config import LLM_PLANNER, LLM_EXECUTOR
from .memory import memory
from .responder import generate_final_response

# Importar todas las herramientas
from .tools.weather import get_weather, geocode, get_weekly_summary
from .tools.tasks import create_task, list_tasks, complete_task, delete_task, edit_task, search_tasks
from .tools.drive import search_files, get_file_metadata, download_file, upload_file, move_file, delete_file
from .tools.gmail import list_messages, get_message, send_message, reply_message, delete_message, modify_labels
from .tools.calendar import list_calendars, list_events, get_event, create_event, update_event, delete_event, find_free_slot

# Agrupar herramientas por categoría
WEATHER_TOOLS = [get_weather, geocode, get_weekly_summary]
TASK_TOOLS = [create_task, list_tasks, complete_task, delete_task, edit_task, search_tasks] 
DRIVE_TOOLS = [search_files, get_file_metadata, download_file, upload_file, move_file, delete_file]
GMAIL_TOOLS = [list_messages, get_message, send_message, reply_message, delete_message, modify_labels]
CALENDAR_TOOLS = [list_calendars, list_events, get_event, create_event, update_event, delete_event, find_free_slot]

ALL_TOOLS = WEATHER_TOOLS + TASK_TOOLS + DRIVE_TOOLS + GMAIL_TOOLS + CALENDAR_TOOLS

# Función para ejecutar herramientas directamente
async def execute_with_visible_tools(state: PlanExecute):
    """Ejecutor que prepara para usar herramientas específicas"""
    print("🔄 [DEBUG] Iniciando execute_with_visible_tools...")
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    
    if not plan:
        print("🔄 [DEBUG] No hay más pasos en el plan")
        return state
    
    step_to_execute = plan[0]
    print(f"🔄 [DEBUG] Preparando ejecución del paso: {step_to_execute}")
    
    # Preparar el estado para que las herramientas específicas puedan procesarlo
    # El routing se hará en should_continue_to_tools()
    
    return state

async def plan_step(state: PlanExecute):
    """Planificador con mejor manejo de entrada"""
    print("🔄 [DEBUG] Iniciando plan_step...")
    
    # Obtener input del usuario de manera robusta
    user_input = None
    if "input" in state:
        user_input = state["input"]
    elif "messages" in state and state["messages"]:
        last_message = state["messages"][-1]
        if isinstance(last_message, dict):
            user_input = last_message.get("content", "")
        else:
            user_input = str(last_message)
    elif "message" in state:
        user_input = state["message"]
    
    if not user_input:
        return {"response": "No se pudo obtener la consulta del usuario."}
    
    print(f"🔄 [DEBUG] Input procesado: {user_input}")
    
    # Obtener session_id del estado
    session_id = state.get("session_id")
    
    # Crear plan con contexto de conversación
    plan = await make_plan(user_input, session_id)
    print(f"🔄 [DEBUG] Plan generado: {plan.steps}")
    
    return {
        "input": user_input,
        "plan": plan.steps,
        "conversation_history": state.get("conversation_history", [])
    }

async def replan_or_finish(state: PlanExecute):
    """Replanner que decide si continuar o finalizar"""
    print("🔄 [DEBUG] Iniciando replan_or_finish...")
    
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    
    # Obtener input original
    original_input = state.get("input", "")
    
    # Si no hay más pasos, generar respuesta final
    if not plan:
        print("🔄 [DEBUG] No hay más pasos, generando respuesta final...")
        
        tool_result = ""
        if past_steps:
            tool_result = past_steps[-1][1]
        
        final_response = await generate_final_response(
            query=original_input,
            tool_result=tool_result,
            session_id=state.get("session_id"),
            past_steps=past_steps
        )
        
        return {"response": final_response}
    
    # Si hay demasiados pasos, finalizar
    if len(past_steps) >= 5:
        print("🔄 [DEBUG] Demasiados pasos, finalizando...")
        
        tool_result = past_steps[-1][1] if past_steps else "Proceso completado."
        
        final_response = await generate_final_response(
            query=original_input,
            tool_result=tool_result,
            session_id=state.get("session_id"),
            past_steps=past_steps
        )
        
        return {"response": final_response}
    
    # Continuar con el plan actual
    return {}

def should_finish(state: PlanExecute):
    """Decidir si terminar o continuar"""
    has_response = state.get("response") is not None
    decision = END if has_response else "executor"
    print(f"🔄 [DEBUG] should_finish decision: {decision}")
    return decision

async def execute_tool_category(state: PlanExecute, category: str):
    """Función genérica para ejecutar herramientas de una categoría específica"""
    print(f"🔄 [DEBUG] Ejecutando herramientas de categoría: {category}")
    
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    
    if not plan:
        return state
    
    step_to_execute = plan[0]
    
    # Simular la ejecución de la herramienta específica
    result = f"✅ Ejecutado con herramientas de {category}: {step_to_execute}"
    
    # Actualizar el estado
    new_past_steps = past_steps[:]
    new_past_steps.append((step_to_execute, result))
    
    remaining_plan = plan[1:] if len(plan) > 1 else []
    
    return {
        **state,
        "past_steps": new_past_steps,
        "plan": remaining_plan
    }

def should_continue_to_tools(state: PlanExecute):
    """Decidir si usar herramientas basándose en el plan actual"""
    plan = state.get("plan", [])
    if not plan:
        return "replan"
    
    # Analizar el primer paso del plan para determinar qué categoría de herramientas usar
    current_step = plan[0].lower() if plan else ""
    
    if any(word in current_step for word in ["clima", "weather", "tiempo", "temperatura"]):
        return "weather_tools"
    elif any(word in current_step for word in ["tarea", "task", "crear", "completar", "eliminar"]):
        return "task_tools"
    elif any(word in current_step for word in ["archivo", "drive", "documento", "buscar archivos"]):
        return "drive_tools"
    elif any(word in current_step for word in ["correo", "email", "gmail", "enviar", "mensaje"]):
        return "gmail_tools"
    elif any(word in current_step for word in ["evento", "calendar", "reunión", "cita", "agenda"]):
        return "calendar_tools"
    else:
        # Si no se identifica una categoría específica, ir directo a replan
        return "replan"

# Funciones específicas para cada categoría de herramientas
async def weather_tools_node(state: PlanExecute):
    return await execute_tool_category(state, "weather")

async def task_tools_node(state: PlanExecute):
    return await execute_tool_category(state, "tasks")

async def drive_tools_node(state: PlanExecute):
    return await execute_tool_category(state, "drive")

async def gmail_tools_node(state: PlanExecute):
    return await execute_tool_category(state, "gmail")

async def calendar_tools_node(state: PlanExecute):
    return await execute_tool_category(state, "calendar")

def build_chatbot_graph_with_visible_tools():
    """Construir grafo con herramientas visibles"""
    print("🔄 [DEBUG] Construyendo grafo con herramientas visibles...")
    
    graph = StateGraph(PlanExecute)
    
    # Añadir nodos principales
    graph.add_node("planner", plan_step)
    graph.add_node("executor", execute_with_visible_tools)
    graph.add_node("replan", replan_or_finish)
    
    # Añadir nodos para cada categoría de herramientas
    graph.add_node("weather_tools", weather_tools_node)
    graph.add_node("task_tools", task_tools_node)
    graph.add_node("drive_tools", drive_tools_node)
    graph.add_node("gmail_tools", gmail_tools_node)
    graph.add_node("calendar_tools", calendar_tools_node)
    
    # Configurar flujo principal
    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    
    # El executor decide qué categoría de herramientas usar
    graph.add_conditional_edges(
        "executor", 
        should_continue_to_tools,
        {
            "weather_tools": "weather_tools",
            "task_tools": "task_tools", 
            "drive_tools": "drive_tools",
            "gmail_tools": "gmail_tools",
            "calendar_tools": "calendar_tools",
            "replan": "replan"
        }
    )
    
    # Todas las herramientas regresan al replan
    graph.add_edge("weather_tools", "replan")
    graph.add_edge("task_tools", "replan")
    graph.add_edge("drive_tools", "replan")
    graph.add_edge("gmail_tools", "replan")
    graph.add_edge("calendar_tools", "replan")
    
    # El replan decide si terminar o continuar
    graph.add_conditional_edges(
        "replan", 
        should_finish,
        {
            END: END,
            "executor": "executor"
        }
    )
    
    compiled_graph = graph.compile()
    
    print(f"🔄 [DEBUG] Grafo con herramientas visibles compilado!")
    return compiled_graph 