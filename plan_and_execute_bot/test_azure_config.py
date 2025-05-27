#!/usr/bin/env python3
"""Script de prueba para verificar la configuración de Azure OpenAI."""
import os
import sys
from dotenv import load_dotenv

def test_azure_config():
    """Probar la configuración de Azure OpenAI."""
    print("🔧 Probando configuración de Azure OpenAI...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Variables requeridas (configuración simplificada)
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    # Verificar variables
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mostrar valor parcial por seguridad
            if "KEY" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    # Verificar variables opcionales
    optional_vars = [
        "AZURE_OPENAI_PLANNER_DEPLOYMENT",
        "AZURE_OPENAI_EXECUTOR_DEPLOYMENT"
    ]
    
    print("\n📋 Variables opcionales:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚪ {var}: No configurada (usará deployment principal)")
    
    if missing_vars:
        print(f"\n❌ Faltan variables de entorno: {', '.join(missing_vars)}")
        print("\n📝 Para tu configuración con gpt-4o-mini, crea un archivo .env con:")
        print("AZURE_OPENAI_API_KEY=tu_clave_azure_openai")
        print("AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/")
        print("AZURE_OPENAI_API_VERSION=2024-02-15-preview")
        print("AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini")
        return False
    
    # Probar importación y configuración
    try:
        print("\n🔄 Probando importación de configuración...")
        from bot.config import settings, LLM_PLANNER, LLM_EXECUTOR
        print("✅ Configuración importada correctamente")
        
        print(f"✅ Deployment principal: {settings.deployment_name}")
        print(f"✅ Planificador usando: {settings.planner_deployment}")
        print(f"✅ Ejecutor usando: {settings.executor_deployment}")
        print(f"✅ Endpoint: {settings.azure_openai_endpoint}")
        print(f"✅ Versión API: {settings.azure_openai_api_version}")
        
        # Verificar si está usando el mismo deployment para ambos
        if settings.planner_deployment == settings.executor_deployment:
            print(f"ℹ️  Usando el mismo deployment ({settings.deployment_name}) para planificador y ejecutor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al importar configuración: {e}")
        return False

def test_simple_call():
    """Hacer una llamada simple para probar conectividad."""
    try:
        print("\n🧪 Probando llamada simple a Azure OpenAI...")
        from bot.config import LLM_PLANNER
        
        response = LLM_PLANNER.invoke("como hacer una hamburguesa")
        print(f"✅ Respuesta recibida: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error en llamada de prueba: {e}")
        print("💡 Verifica que tu deployment 'gpt-4o-mini' esté activo en Azure")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de configuración de Azure OpenAI\n")
    
    # Probar configuración
    config_ok = test_azure_config()
    
    if config_ok:
        print("\n" + "="*50)
        # Probar llamada simple
        call_ok = test_simple_call()
        
        if call_ok:
            print("\n🎉 ¡Todas las pruebas pasaron! Azure OpenAI está configurado correctamente.")
            print("💡 Tu gpt-4o-mini está funcionando para ambos roles (planificador y ejecutor)")
        else:
            print("\n⚠️  Configuración OK, pero hay problemas de conectividad.")
    else:
        print("\n❌ Configuración incompleta. Revisa tu archivo .env")
    
    print("\n📚 Para más información, consulta CONFIGURACION.md") 