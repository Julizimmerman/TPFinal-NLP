"""Configuración centralizada y manejo de variables de entorno para Azure OpenAI."""
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    """Clase para manejar todas las configuraciones del proyecto."""
    
    def __init__(self):
        """Inicializar configuraciones con validaciones."""
        self._validate_required_env_vars()
        
    def _validate_required_env_vars(self):
        """Validar que las variables de entorno requeridas estén presentes."""
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT", 
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT"  # Solo necesitamos un deployment
        ]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Error: Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
            print("💡 Asegúrate de crear un archivo .env con las variables requeridas para Azure OpenAI.")
            print("📝 Ejemplo de archivo .env:")
            print("AZURE_OPENAI_API_KEY=tu_clave_azure_openai")
            print("AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/")
            print("AZURE_OPENAI_API_VERSION=2024-02-15-preview")
            print("AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini")
            print("# Opcional: usar deployments separados")
            print("# AZURE_OPENAI_PLANNER_DEPLOYMENT=gpt-4o-mini")
            print("# AZURE_OPENAI_EXECUTOR_DEPLOYMENT=gpt-4o-mini")
            print("TAVILY_API_KEY=tu_clave_tavily_aqui  # opcional")
            sys.exit(1)
    
    @property
    def azure_openai_api_key(self) -> str:
        """Obtener la clave de API de Azure OpenAI."""
        return os.getenv("AZURE_OPENAI_API_KEY")
    
    @property
    def azure_openai_endpoint(self) -> str:
        """Obtener el endpoint de Azure OpenAI."""
        return os.getenv("AZURE_OPENAI_ENDPOINT")
    
    @property
    def azure_openai_api_version(self) -> str:
        """Obtener la versión de API de Azure OpenAI."""
        return os.getenv("AZURE_OPENAI_API_VERSION")
    
    @property
    def deployment_name(self) -> str:
        """Nombre del deployment principal."""
        return os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    @property
    def planner_deployment(self) -> str:
        """Nombre del deployment para el planificador."""
        # Si hay un deployment específico para el planificador, usarlo
        # Si no, usar el deployment principal
        return os.getenv("AZURE_OPENAI_PLANNER_DEPLOYMENT", self.deployment_name)
    
    @property
    def executor_deployment(self) -> str:
        """Nombre del deployment para el ejecutor."""
        # Si hay un deployment específico para el ejecutor, usarlo
        # Si no, usar el deployment principal
        return os.getenv("AZURE_OPENAI_EXECUTOR_DEPLOYMENT", self.deployment_name)
    
    @property
    def tavily_api_key(self) -> Optional[str]:
        """Obtener la clave de API de Tavily (opcional)."""
        return os.getenv("TAVILY_API_KEY")
    
    @property
    def planner_temperature(self) -> float:
        """Temperatura para el planificador."""
        return float(os.getenv("PLANNER_TEMPERATURE", "0.0"))
    
    @property
    def executor_temperature(self) -> float:
        """Temperatura para el ejecutor."""
        return float(os.getenv("EXECUTOR_TEMPERATURE", "0.2"))
    
    @property
    def max_tokens(self) -> Optional[int]:
        """Máximo número de tokens."""
        max_tokens = os.getenv("MAX_TOKENS")
        return int(max_tokens) if max_tokens else None
    
    @property
    def debug_mode(self) -> bool:
        """Modo debug activado."""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Instancia global de configuración
settings = Settings()

# Variables de configuración para compatibilidad con el código existente
AZURE_OPENAI_API_KEY = settings.azure_openai_api_key

# Configuración de LLMs con Azure OpenAI
LLM_PLANNER = AzureChatOpenAI(
    azure_deployment=settings.planner_deployment,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=settings.planner_temperature,
    max_tokens=settings.max_tokens
)

LLM_EXECUTOR = AzureChatOpenAI(
    azure_deployment=settings.executor_deployment,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version=settings.azure_openai_api_version,
    temperature=settings.executor_temperature,
    max_tokens=settings.max_tokens
)
