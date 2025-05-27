#!/usr/bin/env python3
"""Script de prueba simple para el bot."""
import asyncio
import os
import sys

# Agregar el directorio del bot al path
sys.path.append('plan_and_execute_bot')

async def test_bot():
    """Prueba básica del bot."""
    try:
        print("🔄 [DEBUG] Importando módulos...")
        from bot.graph import build_chatbot_graph
        
        print("🤖 Construyendo el bot...")
        chatbot = build_chatbot_graph()
        
        print("✅ Bot construido exitosamente!")
        print("🧪 Probando con consulta de clima...")
        
        # Prueba simple
        state = {
            "input": "¿Cuál es el clima en Madrid?",
            "past_steps": []
        }
        
        print(f"🔄 [DEBUG] Estado inicial: {state}")
        print("🔄 [DEBUG] Iniciando invocación del chatbot...")
        
        result = await chatbot.ainvoke(state)
        
        print(f"🔄 [DEBUG] Resultado completo: {result}")
        print(f"🎯 Respuesta del bot: {result.get('response', 'Sin respuesta')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"🔄 [DEBUG] Traceback completo:")
        traceback.print_exc()
        print("💡 Asegúrate de tener configurada la variable OPENAI_API_KEY en un archivo .env")

if __name__ == "__main__":
    print("🔄 [DEBUG] Iniciando script de prueba...")
    asyncio.run(test_bot()) 