#!/usr/bin/env python3
"""Script para debuggear cómo se ven las herramientas para el LLM."""
import sys
import json
import inspect

# Agregar el directorio del bot al path
sys.path.append('plan_and_execute_bot')

def get_all_tools():
    """Obtiene todas las herramientas disponibles."""
    tools = []
    
    try:
        # Importar herramientas del archivo principal tools.py
        from bot.tools import get_weather as main_get_weather
        tools.append(("bot.tools", "get_weather", main_get_weather))
        print("✅ Herramientas encontradas en bot.tools")
    except Exception as e:
        print(f"⚠️ Error importando de bot.tools: {e}")
    
    try:
        # Importar herramientas del archivo weather.py
        from bot.tools import weather
        weather_tools = []
        for name, obj in inspect.getmembers(weather):
            if hasattr(obj, 'name') and hasattr(obj, 'description') and callable(obj):
                weather_tools.append(("bot.tools.weather", name, obj))
                tools.append(("bot.tools.weather", name, obj))
        print(f"✅ Herramientas encontradas en bot.tools.weather: {len(weather_tools)}")
    except Exception as e:
        print(f"⚠️ Error importando de bot.tools.weather: {e}")
    
    try:
        # Importar herramientas del archivo tasks.py
        from bot.tools import tasks
        task_tools = []
        for name, obj in inspect.getmembers(tasks):
            if hasattr(obj, 'name') and hasattr(obj, 'description') and callable(obj):
                task_tools.append(("bot.tools.tasks", name, obj))
                tools.append(("bot.tools.tasks", name, obj))
        print(f"✅ Herramientas encontradas en bot.tools.tasks: {len(task_tools)}")
    except Exception as e:
        print(f"⚠️ Error importando de bot.tools.tasks: {e}")
    
    return tools

def inspect_tool(module_name, function_name, tool_func):
    """Inspecciona una herramienta específica."""
    print(f"\n{'='*60}")
    print(f"🔍 HERRAMIENTA: {function_name} (de {module_name})")
    print(f"{'='*60}")
    
    try:
        print(f"📝 Nombre: {getattr(tool_func, 'name', 'N/A')}")
        print(f"📝 Descripción: {getattr(tool_func, 'description', 'N/A')}")
        
        # Información sobre argumentos
        if hasattr(tool_func, 'args'):
            print(f"📝 Args: {tool_func.args}")
        
        # Ver el esquema JSON que se envía al LLM
        if hasattr(tool_func, 'args_schema'):
            print(f"📝 Args schema class: {tool_func.args_schema}")
            if tool_func.args_schema:
                try:
                    schema = tool_func.args_schema.schema()
                    print("📝 Esquema JSON completo:")
                    print(json.dumps(schema, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"⚠️ Error obteniendo esquema: {e}")
        
        # Ver cómo se ve como función de OpenAI
        try:
            from langchain.tools.convert_to_openai import format_tool_to_openai_function
            openai_format = format_tool_to_openai_function(tool_func)
            print("\n🤖 Formato OpenAI Function:")
            print(json.dumps(openai_format, indent=2, ensure_ascii=False))
        except ImportError:
            print("⚠️ No se pudo importar format_tool_to_openai_function")
        except Exception as e:
            print(f"⚠️ Error formateando para OpenAI: {e}")
            
    except Exception as e:
        print(f"❌ Error inspeccionando {function_name}: {e}")
        import traceback
        traceback.print_exc()

def inspect_all_tools():
    """Inspecciona todas las herramientas disponibles."""
    print("🚀 INICIANDO INSPECCIÓN DE TODAS LAS HERRAMIENTAS")
    print("="*60)
    
    tools = get_all_tools()
    
    if not tools:
        print("❌ No se encontraron herramientas para inspeccionar")
        return
    
    print(f"\n📊 RESUMEN: Se encontraron {len(tools)} herramientas")
    for module_name, function_name, _ in tools:
        print(f"  • {function_name} (de {module_name})")
    
    # Inspeccionar cada herramienta
    for module_name, function_name, tool_func in tools:
        inspect_tool(module_name, function_name, tool_func)
    
    print(f"\n{'='*60}")
    print("✅ INSPECCIÓN COMPLETADA")
    print(f"{'='*60}")

if __name__ == "__main__":
    inspect_all_tools() 