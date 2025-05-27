#!/usr/bin/env python3
"""Script de prueba para el sistema de memoria del bot."""
import asyncio
import os
import sys

# Agregar el directorio del bot al path
sys.path.append('plan_and_execute_bot')

async def test_memory_system():
    """Prueba el sistema de memoria con una conversación de seguimiento."""
    try:
        print("🧠 Probando sistema de memoria...")
        from bot.graph import build_chatbot_graph
        from bot.memory import memory
        
        # Construir el bot
        chatbot = build_chatbot_graph()
        
        # Crear una nueva sesión
        session_id = memory.create_session()
        print(f"✅ Sesión creada: {session_id[:8]}...")
        
        # Estado inicial
        state = {
            "session_id": session_id,
            "conversation_history": [],
            "past_steps": []
        }
        
        # Primera consulta
        print("\n🔄 Primera consulta: ¿Cuál es el clima en Madrid?")
        memory.add_message(session_id, "user", "¿Cuál es el clima en Madrid?")
        state["input"] = "¿Cuál es el clima en Madrid?"
        
        result1 = await chatbot.ainvoke(state)
        response1 = result1.get('response', 'Sin respuesta')
        print(f"🤖 Respuesta 1: {response1}")
        
        # Limpiar response para siguiente consulta
        state.pop("response", None)
        
        # Segunda consulta (con referencia a la anterior)
        print("\n🔄 Segunda consulta: ¿Y en Barcelona?")
        memory.add_message(session_id, "user", "¿Y en Barcelona?")
        state["input"] = "¿Y en Barcelona?"
        
        result2 = await chatbot.ainvoke(state)
        response2 = result2.get('response', 'Sin respuesta')
        print(f"🤖 Respuesta 2: {response2}")
        
        # Limpiar response para siguiente consulta
        state.pop("response", None)
        
        # Tercera consulta (referencia implícita)
        print("\n🔄 Tercera consulta: ¿Cuál está más caliente?")
        memory.add_message(session_id, "user", "¿Cuál está más caliente?")
        state["input"] = "¿Cuál está más caliente?"
        
        result3 = await chatbot.ainvoke(state)
        response3 = result3.get('response', 'Sin respuesta')
        print(f"🤖 Respuesta 3: {response3}")
        
        # Mostrar historial completo
        print("\n📝 Historial completo de la conversación:")
        history = memory.get_conversation_history(session_id)
        for i, msg in enumerate(history, 1):
            role_display = "Usuario" if msg['role'] == 'user' else "Asistente"
            print(f"{i}. {role_display}: {msg['content']}")
        
        # Probar contexto para planificación
        print("\n🧠 Contexto para planificación:")
        context = memory.get_context_for_planning(session_id)
        print(context)
        
        print("\n✅ ¡Prueba de memoria completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en prueba de memoria: {e}")
        import traceback
        traceback.print_exc()

async def test_multiple_sessions():
    """Prueba múltiples sesiones independientes."""
    try:
        print("\n🔄 Probando múltiples sesiones...")
        from bot.memory import memory
        
        # Crear dos sesiones
        session1 = memory.create_session()
        session2 = memory.create_session()
        
        # Agregar mensajes a cada sesión
        memory.add_message(session1, "user", "Hola, soy el usuario 1")
        memory.add_message(session1, "assistant", "Hola usuario 1")
        
        memory.add_message(session2, "user", "Hola, soy el usuario 2")
        memory.add_message(session2, "assistant", "Hola usuario 2")
        
        # Verificar que las sesiones son independientes
        history1 = memory.get_conversation_history(session1)
        history2 = memory.get_conversation_history(session2)
        
        print(f"📝 Sesión 1 tiene {len(history1)} mensajes")
        print(f"📝 Sesión 2 tiene {len(history2)} mensajes")
        
        # Mostrar resúmenes
        summary1 = memory.get_session_summary(session1)
        summary2 = memory.get_session_summary(session2)
        
        print(f"📊 Resumen sesión 1: {summary1}")
        print(f"📊 Resumen sesión 2: {summary2}")
        
        print("✅ Prueba de múltiples sesiones completada!")
        
    except Exception as e:
        print(f"❌ Error en prueba de múltiples sesiones: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de memoria\n")
    asyncio.run(test_memory_system())
    asyncio.run(test_multiple_sessions())
    print("\n🎉 ¡Todas las pruebas completadas!") 