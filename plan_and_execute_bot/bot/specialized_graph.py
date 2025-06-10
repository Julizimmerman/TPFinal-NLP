"""Grafo principal que coordina orquestadores especializados."""
from langgraph.graph import StateGraph, END
from .schemas import PlanExecute
from .orchestrators.main_orchestrator import (
    main_orchestrator_node, 
    route_to_specialist, 
    general_response_node
)
from .orchestrators.gmail_orchestrator import gmail_orchestrator_node
from .orchestrators.tasks_orchestrator import tasks_orchestrator_node
from .orchestrators.calendar_orchestrator import calendar_orchestrator_node
from .orchestrators.drive_orchestrator import drive_orchestrator_node
from .orchestrators.weather_orchestrator import weather_orchestrator_node

def build_specialized_chatbot_graph():
    """Construye el grafo principal con orquestadores especializados."""
    
    print("🎯 [SPECIALIZED_GRAPH] Construyendo grafo con orquestadores especializados...")
    
    graph = StateGraph(PlanExecute)
    
    # Nodo principal de clasificación e routing
    graph.add_node("main_orchestrator", main_orchestrator_node)
    
    # Orquestadores especializados para cada servicio
    graph.add_node("gmail_orchestrator", gmail_orchestrator_node)
    graph.add_node("tasks_orchestrator", tasks_orchestrator_node)
    graph.add_node("calendar_orchestrator", calendar_orchestrator_node)
    graph.add_node("drive_orchestrator", drive_orchestrator_node)
    graph.add_node("weather_orchestrator", weather_orchestrator_node)
    
    # Nodo para respuestas generales
    graph.add_node("general_response", general_response_node)
    
    # Configurar flujo principal
    graph.set_entry_point("main_orchestrator")
    
    # Routing condicional desde el orquestador principal
    graph.add_conditional_edges(
        "main_orchestrator",
        route_to_specialist,
        {
            "gmail_orchestrator": "gmail_orchestrator",
            "tasks_orchestrator": "tasks_orchestrator", 
            "calendar_orchestrator": "calendar_orchestrator",
            "drive_orchestrator": "drive_orchestrator",
            "weather_orchestrator": "weather_orchestrator",
            "general_response": "general_response"
        }
    )
    
    # Todos los orquestadores especializados terminan en END
    graph.add_edge("gmail_orchestrator", END)
    graph.add_edge("tasks_orchestrator", END)
    graph.add_edge("calendar_orchestrator", END)
    graph.add_edge("drive_orchestrator", END)
    graph.add_edge("weather_orchestrator", END)
    graph.add_edge("general_response", END)
    
    compiled_graph = graph.compile()
    
    print("🎯 [SPECIALIZED_GRAPH] Grafo compilado exitosamente!")
    print("📋 [SPECIALIZED_GRAPH] Servicios disponibles:")
    print("  📧 Gmail Orchestrator")
    print("  📋 Tasks Orchestrator") 
    print("  📅 Calendar Orchestrator")
    print("  📁 Drive Orchestrator")
    print("  🌤️ Weather Orchestrator")
    print("  💬 General Response")
    
    return compiled_graph 