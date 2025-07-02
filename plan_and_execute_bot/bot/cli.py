"""Tiny REPL so you can chat from the terminal."""
import asyncio
from .graph import build_chatbot_graph
from .memory import memory

chatbot = build_chatbot_graph()

async def chat():
    """Interfaz de chat con memoria de conversación."""
    # Crear una nueva sesión de conversación
    session_id = memory.create_session()
    print(f"🧠 Nueva sesión de conversación iniciada: {session_id[:8]}...")
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
            # Crear nueva sesión
            session_id = memory.create_session()
            state = {
                "session_id": session_id,
                "conversation_history": [],
                "past_steps": []
            }
            print(f"🧠 Nueva sesión iniciada: {session_id[:8]}...")
            continue
        elif user_input == '/historial':
            # Mostrar historial de la conversación actual (últimos 5 mensajes)
            history = memory.get_conversation_history(session_id, limit=5)
            if not history:
                print("📝 No hay historial en esta conversación.")
            else:
                print("📝 Historial de conversación (últimos 5 mensajes):")
                for msg in history:
                    role_display = "Usuario" if msg['role'] == 'user' else "Asistente"
                    timestamp = msg['timestamp'][:19]  # Solo fecha y hora
                    print(f"  [{timestamp}] {role_display}: {msg['content']}")
            continue
        elif user_input == '/sesiones':
            # Listar todas las sesiones
            sessions = memory.list_sessions()
            if not sessions:
                print("📝 No hay sesiones guardadas.")
            else:
                print("📝 Sesiones disponibles:")
                for sid in sessions:
                    summary = memory.get_session_summary(sid)
                    if summary.get('message_count', 0) > 0:
                        first_msg = summary.get('first_user_message', 'Sin mensajes')[:50]
                        print(f"  {sid[:8]}... ({summary['message_count']} mensajes) - {first_msg}...")
            continue
        elif not user_input:
            continue

        # Guardar mensaje del usuario en memoria
        memory.add_message(session_id, "user", user_input)
        
        # Actualizar estado con la nueva entrada
        state["input"] = user_input
        
        try:
            # Procesar con el chatbot
            print("🤔 Pensando...")
            state = await chatbot.ainvoke(state)
            
            # Mostrar respuesta
            response = state.get("response", "No pude generar una respuesta.")
            print("Bot >", response)
            
            # Limpiar response del estado para la siguiente iteración
            state.pop("response", None)
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print("Bot >", error_msg)
            # Guardar error en memoria también
            memory.add_message(session_id, "assistant", error_msg)

if __name__ == "__main__":
    asyncio.run(chat())
