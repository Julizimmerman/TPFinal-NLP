# Sistema de Ejecutores Especializados

Este directorio contiene el sistema de ejecutores especializados que reemplaza el executor general anterior.

## Arquitectura

### 1. Router (`router.py`)
- **Función**: Decide qué ejecutor especializado usar basándose en el contenido de la tarea
- **Entrada**: Tarea del usuario
- **Salida**: Nombre del ejecutor especializado apropiado
- **Lógica**: Análisis semántico de la tarea para determinar el tipo de operación

### 2. Ejecutores Especializados

#### `weather_executor.py`
- **Propósito**: Maneja todas las tareas relacionadas con clima y meteorología
- **Herramientas**: get_weather, geocode, get_air_quality, get_sun_times, get_clothing_advice, get_weekly_summary, get_next_rain_day
- **Prompt**: Especializado en información meteorológica con instrucciones detalladas sobre cómo usar cada herramienta

#### `tasks_executor.py`
- **Propósito**: Maneja todas las tareas relacionadas con Google Tasks
- **Herramientas**: create_task, list_tasks, complete_task, delete_task, edit_task, search_tasks, add_subtask
- **Prompt**: Especializado en gestión de tareas con instrucciones específicas sobre parámetros y uso

#### `drive_executor.py`
- **Propósito**: Maneja todas las tareas relacionadas con Google Drive
- **Herramientas**: search_files, get_file_metadata, download_file, upload_file, move_file, delete_file
- **Prompt**: Especializado en gestión de archivos con instrucciones sobre operaciones de archivos

#### `gmail_executor.py`
- **Propósito**: Maneja todas las tareas relacionadas con Gmail
- **Herramientas**: list_messages, get_message, send_message, reply_message, delete_message, modify_labels
- **Prompt**: Especializado en gestión de correo electrónico con instrucciones sobre construcción de emails y gestión de etiquetas

#### `calendar_executor.py`
- **Propósito**: Maneja todas las tareas relacionadas con Google Calendar
- **Herramientas**: list_calendars, list_events, get_event, create_event, update_event, delete_event
- **Prompt**: Especializado en gestión de calendarios con instrucciones sobre fechas, asistentes y eventos

### 3. Ejecutor Principal (`specialized_executor.py`)
- **Función**: Coordina todos los ejecutores especializados
- **Proceso**:
  1. Recibe una tarea
  2. Consulta el router para determinar qué ejecutor usar
  3. Invoca el ejecutor especializado apropiado
  4. Retorna el resultado

## Ventajas del Sistema

### 1. Especialización
- Cada ejecutor tiene un prompt específico y detallado para su dominio
- Mejor comprensión de las herramientas disponibles
- Respuestas más precisas y estructuradas

### 2. Mantenibilidad
- Fácil agregar nuevos ejecutores especializados
- Separación clara de responsabilidades
- Código más organizado y modular

### 3. Escalabilidad
- Cada ejecutor puede evolucionar independientemente
- Fácil testing individual de cada ejecutor
- Posibilidad de optimizar cada ejecutor por separado

### 4. Claridad en Respuestas
- Cada ejecutor tiene un formato de respuesta estructurado:
  1. "Voy a usar [HERRAMIENTA] para [PROPÓSITO]"
  2. "Resultado: [DESCRIPCIÓN CLARA DEL RESULTADO]"
  3. "Estado: [EXITOSO/FRACASO] - [EXPLICACIÓN]"

## Uso

### Ejecutor Principal
```python
from plan_and_execute_bot.bot.executors import execute_specialized_task

# El sistema automáticamente selecciona el ejecutor apropiado
result = await execute_specialized_task("¿Cuál es el clima en Madrid?")
```

### Ejecutores Individuales
```python
from plan_and_execute_bot.bot.executors import execute_weather_task

# Usar un ejecutor específico directamente
result = await execute_weather_task("Obtener el clima en Barcelona")
```

### Router
```python
from plan_and_execute_bot.bot.executors import route_task

# Obtener qué ejecutor se usaría para una tarea
executor_name = await route_task("Crear una tarea llamada 'Reunión'")
# Retorna: "tasks_executor"
```

## Configuración

Cada ejecutor utiliza:
- **LLM**: `LLM_EXECUTOR` desde `config.py`
- **Fecha actual**: Interpolada automáticamente en los prompts
- **Herramientas**: Importadas desde el directorio `tools/`
- **Configuración**: Agente LangChain con parámetros optimizados

## Testing

Ver `test/test_specialized_executors.py` para ejemplos de cómo probar cada ejecutor.

## Migración desde el Sistema Anterior

El sistema anterior usaba un solo executor general con todas las herramientas. El nuevo sistema:

1. **Mantiene compatibilidad**: El `agent_executor` en `executor.py` ahora usa los ejecutores especializados
2. **Mejora la experiencia**: Respuestas más claras y estructuradas
3. **Facilita el mantenimiento**: Cada dominio tiene su propio ejecutor especializado
4. **Permite evolución independiente**: Cada ejecutor puede mejorar sin afectar a los demás 