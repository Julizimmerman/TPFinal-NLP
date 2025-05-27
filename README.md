# Plan and Execute Bot

Un bot conversacional que utiliza LangGraph para planificar y ejecutar tareas paso a paso, **ahora con memoria de conversación**.

## Características

- **Planificación**: Descompone consultas complejas en pasos simples
- **Ejecución**: Ejecuta cada paso usando herramientas disponibles
- **Re-planificación**: Ajusta el plan basándose en los resultados obtenidos
- **🧠 Memoria de Conversación**: Recuerda el contexto de conversaciones anteriores
- **📝 Persistencia**: Guarda el historial en archivo JSON
- **🔄 Sesiones Múltiples**: Maneja múltiples conversaciones independientes

## Funcionalidades de Memoria

### Contexto de Conversación
El bot ahora puede:
- Recordar mensajes anteriores en la misma sesión
- Entender referencias como "esa ciudad", "el clima que pregunté antes"
- Mantener contexto para preguntas de seguimiento
- Planificar considerando el historial de la conversación

### Comandos de Chat
- `/nueva` - Iniciar una nueva conversación
- `/historial` - Ver el historial de la conversación actual
- `/sesiones` - Listar todas las sesiones guardadas
- `salir`, `exit`, `quit` - Terminar el chat

### Ejemplos de Conversación con Memoria
```
You > ¿Cuál es el clima en Madrid?
Bot > Madrid: 22°C, soleado con algunas nubes...

You > ¿Y en Barcelona?
Bot > Barcelona: 25°C, despejado...

You > ¿Cuál está más caliente?
Bot > Según la información anterior, Barcelona está más caliente (25°C) que Madrid (22°C).
```

## Herramientas Disponibles

- `get_weather(location)`: Obtiene información del clima actual
- `get_next_rain_day(location)`: Próximo día con lluvia
- `get_weekly_summary(location)`: Resumen del clima de 5 días
- `get_clothing_advice(location)`: Recomendaciones de vestimenta
- `geocode(location)`: Obtener coordenadas de una ubicación
- `get_air_quality(location)`: Calidad del aire
- `get_sun_times(location)`: Horarios de amanecer y atardecer

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

### Chat Interactivo con Memoria
```bash
python main.py
```

### Ejemplo de Conversación Completa
```
🧠 Nueva sesión de conversación iniciada: 12345678...
💡 Escribe 'salir', 'exit' o presiona Ctrl+C para terminar
💡 Escribe '/nueva' para iniciar una nueva conversación
💡 Escribe '/historial' para ver el historial de la conversación
--------------------------------------------------

You > ¿Cuál es el clima en Madrid?
🤔 Pensando...
Bot > Madrid: 22°C, soleado con algunas nubes. Viento suave del oeste a 10 km/h. Humedad: 45%

You > ¿Y qué tal Barcelona?
🤔 Pensando...
Bot > Barcelona: 25°C, despejado. Viento del este a 15 km/h. Humedad: 60%

You > ¿Cuál de las dos ciudades está más caliente?
🤔 Pensando...
Bot > Según la información del clima que consulté anteriormente, Barcelona está más caliente con 25°C comparado con Madrid que tiene 22°C.

You > /historial
📝 Historial de conversación:
  [2024-01-15 10:30:15] Usuario: ¿Cuál es el clima en Madrid?
  [2024-01-15 10:30:18] Asistente: Madrid: 22°C, soleado con algunas nubes...
  [2024-01-15 10:31:20] Usuario: ¿Y qué tal Barcelona?
  [2024-01-15 10:31:23] Asistente: Barcelona: 25°C, despejado...
  [2024-01-15 10:32:10] Usuario: ¿Cuál de las dos ciudades está más caliente?
  [2024-01-15 10:32:13] Asistente: Según la información del clima que consulté...

You > salir
👋 ¡Hasta luego!
```

## Estructura del Proyecto

- `bot/config.py`: Configuración de LLMs y herramientas
- `bot/tools/`: Herramientas disponibles para el executor
- `bot/executor.py`: Agente que ejecuta pasos individuales
- `bot/planner.py`: Módulo de planificación con contexto
- `bot/graph.py`: Grafo principal que coordina todo el flujo
- `bot/cli.py`: Interfaz de línea de comandos con memoria
- `bot/memory.py`: **Sistema de memoria de conversación**
- `bot/schemas.py`: Esquemas de datos con campos de memoria
- `conversation_memory.json`: **Archivo de persistencia de memoria**

## Pruebas

### Probar Configuración
```bash
python test/test_azure_config.py
```

### Probar Sistema de Memoria
```bash
python test/test_memory.py
```

### Probar Bot Completo
```bash
python test/test_bot.py
```

## Archivos de Memoria

El sistema crea automáticamente un archivo `conversation_memory.json` que contiene:
- Todas las sesiones de conversación
- Historial completo de mensajes
- Timestamps de cada mensaje
- Metadatos de sesiones

**Nota**: Este archivo se guarda automáticamente después de cada mensaje y se carga al iniciar el bot.

## Configuración Avanzada

Ver `CONFIGURACION.md` para detalles completos sobre:
- Variables de entorno de Azure OpenAI
- Configuración de deployments
- Parámetros de temperatura y tokens
- Modo debug