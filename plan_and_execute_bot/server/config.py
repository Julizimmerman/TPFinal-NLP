from os import environ
import logging
import sys

LOGGER = logging.getLogger(__name__)

# Configuración de LangGraph
LANGGRAPH_URL = environ.get("LANGGRAPH_URL", "http://localhost:2024")
ASSISTANT_ID = environ.get("LANGGRAPH_ASSISTANT_ID", "agent")
CONFIG = environ.get("CONFIG") or "{}"

# Configuración de Twilio
TWILIO_AUTH_TOKEN = environ.get("TWILIO_AUTH_TOKEN")
TWILIO_ACCOUNT_SID = environ.get("TWILIO_ACCOUNT_SID")
# Para sandbox no necesitas número específico - Twilio maneja esto automáticamente
TWILIO_WHATSAPP_NUMBER = environ.get("TWILIO_WHATSAPP_NUMBER", "sandbox")

# Configuración de logs
LOG_LEVEL = environ.get("LOG_LEVEL", "INFO")
DEBUG = environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

# Validación de configuración crítica
def validate_config():
    """Validar que las configuraciones críticas estén presentes."""
    missing_vars = []
    
    # Variables críticas para Twilio
    if not TWILIO_ACCOUNT_SID:
        missing_vars.append("TWILIO_ACCOUNT_SID")
    if not TWILIO_AUTH_TOKEN:
        missing_vars.append("TWILIO_AUTH_TOKEN")
    
    # Variables críticas para LangGraph
    if not LANGGRAPH_URL:
        missing_vars.append("LANGGRAPH_URL")
    
    if missing_vars:
        LOGGER.error(f"❌ Faltan variables de entorno críticas: {', '.join(missing_vars)}")
        LOGGER.error("💡 Asegúrate de crear un archivo .env con las variables requeridas")
        LOGGER.error("📝 Ver env_example.txt para un ejemplo completo")
        sys.exit(1)
    
    LOGGER.info("✅ Configuración validada correctamente")

# Validar configuración al importar
validate_config()