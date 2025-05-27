# Plan and Execute Bot

Un bot conversacional que utiliza LangGraph para planificar y ejecutar tareas paso a paso.

## Características

- **Planificación**: Descompone consultas complejas en pasos simples
- **Ejecución**: Ejecuta cada paso usando herramientas disponibles
- **Re-planificación**: Ajusta el plan basándose en los resultados obtenidos

## Herramientas Disponibles

- `get_weather(location)`: Obtiene información del clima (siempre retorna "100")

## Instalación

1. Instalar dependencias:
```bash
cd plan_and_execute_bot
pip install -r requirements.txt
```

2. Configurar variables de entorno:
```bash
# Crear archivo .env con tu configuración de Azure OpenAI
AZURE_OPENAI_API_KEY=tu_clave_azure_openai
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_PLANNER_DEPLOYMENT=gpt-4
AZURE_OPENAI_EXECUTOR_DEPLOYMENT=gpt-35-turbo
TAVILY_API_KEY=tu_clave_tavily_aqui  # opcional para esta versión
```

## Uso

Ejecutar el bot:
```bash
python main.py
```

Ejemplo de conversación:
```
You > ¿Cuál es el clima en Madrid?
Bot > El clima en Madrid es 100
```

## Estructura del Proyecto

- `bot/config.py`: Configuración de LLMs y herramientas
- `bot/tools.py`: Herramientas disponibles para el executor
- `bot/executor.py`: Agente que ejecuta pasos individuales
- `bot/planner.py`: Módulo de planificación
- `bot/graph.py`: Grafo principal que coordina todo el flujo
- `bot/cli.py`: Interfaz de línea de comandos