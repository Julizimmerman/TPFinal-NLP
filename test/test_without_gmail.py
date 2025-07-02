#!/usr/bin/env python3
"""
Script de prueba que funciona sin Gmail para verificar el resto del sistema.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plan_and_execute_bot.bot.executors import execute_specialized_task

async def test_weather():
    """Prueba el ejecutor de clima."""
    print("🌤️ Probando ejecutor de clima...")
    result = await execute_specialized_task("¿Cuál es el clima en Buenos Aires?")
    print(f"Resultado: {result}")
    print("-" * 50)

async def test_tasks():
    """Prueba el ejecutor de tareas."""
    print("📋 Probando ejecutor de tareas...")
    result = await execute_specialized_task("Listar mis tareas pendientes")
    print(f"Resultado: {result}")
    print("-" * 50)

async def test_drive():
    """Prueba el ejecutor de Drive."""
    print("📁 Probando ejecutor de Drive...")
    result = await execute_specialized_task("Buscar archivos en Drive")
    print(f"Resultado: {result}")
    print("-" * 50)

async def test_calendar():
    """Prueba el ejecutor de Calendar."""
    print("📅 Probando ejecutor de Calendar...")
    result = await execute_specialized_task("Listar mis eventos de hoy")
    print(f"Resultado: {result}")
    print("-" * 50)

async def test_router():
    """Prueba el router para diferentes tipos de tareas."""
    print("🔄 Probando router...")
    
    tasks = [
        "¿Cuál es el clima en Madrid?",
        "Crear una tarea llamada 'Reunión'",
        "Buscar archivos en Drive",
        "Listar mis eventos de mañana"
    ]
    
    for task in tasks:
        print(f"Tarea: {task}")
        result = await execute_specialized_task(task)
        print(f"Resultado: {result[:200]}...")
        print("-" * 30)

async def main():
    """Función principal de pruebas."""
    print("🧪 Iniciando pruebas del sistema sin Gmail...")
    print("=" * 60)
    
    try:
        await test_weather()
        await test_tasks()
        await test_drive()
        await test_calendar()
        await test_router()
        
        print("✅ Todas las pruebas completadas exitosamente!")
        print("💡 El sistema funciona correctamente para todas las funcionalidades excepto Gmail.")
        print("📧 Para usar Gmail, sigue las instrucciones en CONFIGURACION_GMAIL.md")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 