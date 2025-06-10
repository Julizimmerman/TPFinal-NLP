"""Chat específico para orquestadores especializados."""
import asyncio
from bot.specialized_graph import build_specialized_chatbot_graph
from bot.memory import memory

async def specialized_chat():
    """Chat usando orquestadores especializados."""
    
    print("🎯 CHAT CON ORQUESTADORES ESPECIALIZADOS")
    print("=" * 50)
    print("📧 Gmail | 📋 Tasks | 📅 Calendar | 📁 Drive | 🌤️ Weather | 💬 General")
    print("=" * 50)
    
    # Construir el grafo especializado
    chatbot = build_specialized_chatbot_graph()
    
    # Crear una nueva sesión de conversación
    session_id = memory.create_session()
    print(f"🧠 Nueva sesión iniciada: {session_id[:8]}...")
    print("💡 Escribe 'salir', 'exit' o presiona Ctrl+C para terminar")
    print("💡 Escribe '/nueva' para iniciar una nueva conversación")
    print("💡 Escribe '/historial' para ver el historial de la conversación")
    print("-" * 50)
    
    state = {
        "session_id": session_id,
        "conversation_history": [],
        "past_steps": []
    }
    
    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break

        # Comandos especiales
        if user_input.lower() in ['salir', 'exit', 'quit']:
            print("👋 ¡Hasta luego!")
            break
        elif user_input == '/nueva':
            session_id = memory.create_session()
            state = {
                "session_id": session_id,
                "conversation_history": [],
                "past_steps": []
            }
            print(f"🧠 Nueva sesión iniciada: {session_id[:8]}...")
            continue
        elif user_input == '/historial':
            history = memory.get_conversation_history(session_id)
            if not history:
                print("📝 No hay historial en esta conversación.")
            else:
                print("📝 Historial de conversación:")
                for msg in history:
                    role_display = "Usuario" if msg['role'] == 'user' else "Asistente"
                    timestamp = msg['timestamp'][:19]
                    print(f"  [{timestamp}] {role_display}: {msg['content']}")
            continue
        elif user_input == '/ayuda':
            print("🎯 SERVICIOS DISPONIBLES:")
            print("📧 Gmail: 'Envía un correo a...', 'Revisa mi bandeja'")
            print("📋 Tasks: 'Agrega ... a mi lista', '¿Cuáles son mis tareas?'")
            print("📅 Calendar: 'Crea una reunión...', '¿Qué tengo programado?'")
            print("📁 Drive: 'Busca el documento...', '¿Dónde está mi...?'")
            print("🌤️ Weather: '¿Cómo está el clima en...?', '¿Va a llover?'")
            print("💬 General: Conversación normal")
            continue
        elif not user_input:
            continue

        # Guardar mensaje del usuario en memoria
        memory.add_message(session_id, "user", user_input)
        
        # Actualizar estado con la nueva entrada
        state["input"] = user_input
        
        try:
            # Procesar con el chatbot especializado
            print("🎯 Analizando y redirigiendo...")
            state = await chatbot.ainvoke(state)
            
            # Mostrar respuesta
            response = state.get("response", "No pude generar una respuesta.")
            intent = state.get("intent", "")
            
            # Mostrar el servicio que se usó
            service_emoji = {
                "GMAIL": "📧",
                "TASKS": "📋", 
                "CALENDAR": "📅",
                "DRIVE": "📁",
                "WEATHER": "🌤️",
                "GENERAL": "💬"
            }
            emoji = service_emoji.get(intent, "🤖")
            
            print(f"{emoji} Bot > {response}")
            
            # Limpiar response del estado para la siguiente iteración
            state.pop("response", None)
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print("Bot >", error_msg)
            memory.add_message(session_id, "assistant", error_msg)

if __name__ == "__main__":
    asyncio.run(specialized_chat()) 