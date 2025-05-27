#!/usr/bin/env python3
"""Script para debuggear cómo se ven las herramientas para el LLM."""
import sys
import json

# Agregar el directorio del bot al path
sys.path.append('plan_and_execute_bot')

def inspect_tool():
    """Inspecciona cómo se ve la herramienta para el LLM."""
    try:
        from bot.tools import get_weather
        
        print("🔍 Inspeccionando la herramienta get_weather...")
        print(f"📝 Nombre: {get_weather.name}")
        print(f"📝 Descripción: {get_weather.description}")
        print(f"📝 Args schema: {get_weather.args}")
        
        # Ver el esquema JSON que se envía al LLM
        if hasattr(get_weather, 'args_schema'):
            print(f"📝 Args schema class: {get_weather.args_schema}")
            if get_weather.args_schema:
                schema = get_weather.args_schema.schema()
                print("📝 Esquema JSON completo:")
                print(json.dumps(schema, indent=2, ensure_ascii=False))
        
        # Ver cómo se ve como función de OpenAI
        try:
            from langchain.tools.convert_to_openai import format_tool_to_openai_function
            openai_format = format_tool_to_openai_function(get_weather)
            print("\n🤖 Formato OpenAI Function:")
            print(json.dumps(openai_format, indent=2, ensure_ascii=False))
        except ImportError:
            print("⚠️ No se pudo importar format_tool_to_openai_function")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_tool() 