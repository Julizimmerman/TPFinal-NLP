"""Script de prueba para los orquestadores especializados."""
import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from bot.specialized_graph import build_specialized_chatbot_graph
from bot.schemas import PlanExecute

async def test_orchestrators():
    """Prueba los orquestadores especializados con diferentes tipos de consultas."""
    
    print("🎯 Iniciando pruebas de orquestadores especializados...\n")
    
    # Construir el grafo
    graph = build_specialized_chatbot_graph()
    
    # Casos de prueba
    test_cases = [
        # Gmail
        ("Envía un correo a test@example.com", "GMAIL"),
        ("Revisa mi bandeja de entrada", "GMAIL"),
        
        # Tasks
        ("Agrega comprar leche a mi lista", "TASKS"),
        ("¿Cuáles son mis tareas pendientes?", "TASKS"),
        
        # Calendar
        ("Crea una reunión para mañana a las 3pm", "CALENDAR"),
        ("¿Qué tengo programado hoy?", "CALENDAR"),
        
        # Drive
        ("Busca el documento de presupuesto", "DRIVE"),
        ("¿Dónde está mi presentación?", "DRIVE"),
        
        # Weather
        ("¿Cómo está el clima en Madrid?", "WEATHER"),
        ("¿Va a llover mañana?", "WEATHER"),
        
        # General
        ("Hola, ¿cómo estás?", "GENERAL"),
        ("¿Qué puedes hacer?", "GENERAL"),
    ]
    
    for i, (query, expected_service) in enumerate(test_cases, 1):
        print(f"📝 Prueba {i}: {query}")
        print(f"   Servicio esperado: {expected_service}")
        
        try:
            # Ejecutar el grafo
            state = PlanExecute(
                input=query,
                session_id="test_session_123"
            )
            
            print(f"   Estado inicial: {dict(state)}")
            
            result = await graph.ainvoke(state)
            
            # Mostrar resultado completo
            print(f"   Estado final: {dict(result)}")
            
            response = result.get("response", "Sin respuesta")
            intent = result.get("intent", "Sin intención")
            
            print(f"   Intención detectada: {intent}")
            print(f"   Respuesta: {response[:100]}...")
            
            # Verificar si la intención es correcta
            status = "✅" if intent == expected_service else "❌"
            print(f"   {status} {'Correcto' if intent == expected_service else 'Incorrecto'}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("-" * 50)
    
    print("🎯 Pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(test_orchestrators()) 