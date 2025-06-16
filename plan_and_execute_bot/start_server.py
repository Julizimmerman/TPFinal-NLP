#!/usr/bin/env python3
"""
Script de inicio para el servidor WhatsApp Bot.
Inicia el servidor FastAPI con configuración personalizada.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Iniciar el servidor con configuración personalizada."""
    
    # Configuración del servidor
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    
    print("🚀 Iniciando Plan & Execute Bot - Servidor WhatsApp")
    print(f"🌐 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🐛 Debug: {debug}")
    print("="*50)
    
    try:
        # Iniciar servidor
        uvicorn.run(
            "server.server:APP",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 