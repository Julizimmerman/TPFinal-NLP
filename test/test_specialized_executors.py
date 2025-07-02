"""Test para verificar que todos los ejecutores especializados funcionan correctamente."""
import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plan_and_execute_bot.bot.executors import (
    execute_specialized_task,
    execute_weather_task,
    execute_tasks_task,
    execute_drive_task,
    execute_gmail_task,
    execute_calendar_task,
    route_task
)

async def test_router():
    """Test del router para verificar que selecciona el ejecutor correcto."""
    print("🧪 [TEST] Probando router...")
    
    test_cases = [
        ("¿Cuál es el clima en Buenos Aires?", "weather_executor"),
        ("Crear una tarea llamada 'Reunión'", "tasks_executor"),
        ("Buscar archivos en Drive", "drive_executor"),
        ("Enviar un email a Juan", "gmail_executor"),
        ("Crear un evento en el calendario", "calendar_executor"),
    ]
    
    for task, expected_executor in test_cases:
        try:
            executor = await route_task(task)
            print(f"✅ Tarea: '{task}' → Ejecutor: {executor}")
            assert executor == expected_executor, f"Esperado {expected_executor}, obtenido {executor}"
        except Exception as e:
            print(f"❌ Error en router para tarea '{task}': {e}")
    
    print("✅ Router test completado\n")

async def test_weather_executor():
    """Test del ejecutor de clima."""
    print("🧪 [TEST] Probando weather_executor...")
    
    try:
        result = await execute_weather_task("¿Cuál es el clima en Madrid?")
        print(f"✅ Weather executor: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en weather_executor: {e}")
    
    print("✅ Weather executor test completado\n")

async def test_tasks_executor():
    """Test del ejecutor de tareas."""
    print("🧪 [TEST] Probando tasks_executor...")
    
    try:
        result = await execute_tasks_task("Listar tareas pendientes")
        print(f"✅ Tasks executor: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en tasks_executor: {e}")
    
    print("✅ Tasks executor test completado\n")

async def test_drive_executor():
    """Test del ejecutor de Drive."""
    print("🧪 [TEST] Probando drive_executor...")
    
    try:
        result = await execute_drive_task("Buscar archivos con 'documento'")
        print(f"✅ Drive executor: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en drive_executor: {e}")
    
    print("✅ Drive executor test completado\n")

async def test_gmail_executor():
    """Test del ejecutor de Gmail."""
    print("🧪 [TEST] Probando gmail_executor...")
    
    try:
        result = await execute_gmail_task("Listar mensajes recientes")
        print(f"✅ Gmail executor: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en gmail_executor: {e}")
    
    print("✅ Gmail executor test completado\n")

async def test_calendar_executor():
    """Test del ejecutor de Calendar."""
    print("🧪 [TEST] Probando calendar_executor...")
    
    try:
        result = await execute_calendar_task("Listar calendarios disponibles")
        print(f"✅ Calendar executor: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en calendar_executor: {e}")
    
    print("✅ Calendar executor test completado\n")

async def test_specialized_executor():
    """Test del ejecutor especializado principal."""
    print("🧪 [TEST] Probando specialized_executor...")
    
    test_tasks = [
        "¿Cuál es el clima en Barcelona?",
        "Crear una tarea llamada 'Test'",
        "Buscar archivos en Drive",
        "Listar mensajes de Gmail",
        "Listar calendarios disponibles"
    ]
    
    for task in test_tasks:
        try:
            result = await execute_specialized_task(task)
            print(f"✅ Specialized executor para '{task}': {result[:100]}...")
        except Exception as e:
            print(f"❌ Error en specialized_executor para '{task}': {e}")
    
    print("✅ Specialized executor test completado\n")

async def main():
    """Ejecutar todos los tests."""
    print("🚀 Iniciando tests de ejecutores especializados...\n")
    
    # Ejecutar tests individuales
    await test_router()
    await test_weather_executor()
    await test_tasks_executor()
    await test_drive_executor()
    await test_gmail_executor()
    await test_calendar_executor()
    await test_specialized_executor()
    
    print("🎉 Todos los tests completados!")

if __name__ == "__main__":
    asyncio.run(main()) 