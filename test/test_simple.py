#!/usr/bin/env python3
"""Script de prueba simple y rápido."""
import sys
import os

# Agregar el directorio del bot al path
sys.path.append('plan_and_execute_bot')

def test_weather_tool():
    """Prueba solo la herramienta de clima."""
    try:
        from bot.tools import get_weather
        
        print("🧪 Probando herramienta de clima...")
        result = get_weather("Madrid")
        print(f"✅ Resultado: {result}")
        
        result2 = get_weather("Barcelona")
        print(f"✅ Resultado: {result2}")
        
        result3 = get_weather("Ciudad desconocida")
        print(f"✅ Resultado: {result3}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weather_tool() 