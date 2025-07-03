# 🤖 Plan & Execute Bot - Asistente Inteligente Multifuncional

Un bot conversacional avanzado basado en **LangGraph** que combina planificación inteligente con ejecución especializada de tareas. El bot puede interactuar a través de **CLI**, **LangGraph Studio** y **WhatsApp** via Twilio.

## 🚀 Funcionalidades Principales

### 🧠 Sistema de Planificación y Ejecución
- **Planificador Inteligente**: Analiza consultas y crea planes estructurados
- **Ejecutores Especializados**: 5 ejecutores dedicados para diferentes dominios
- **Re-planificación Automática**: Adapta el plan según los resultados obtenidos
- **Memoria Conversacional**: Mantiene contexto entre sesiones

### 🌤️ Herramientas Disponibles (26 herramientas)

#### **Clima y Meteorología** (7 herramientas)
- `get_weather`: Información meteorológica actual
- `geocode`: Geocodificación de ubicaciones
- `get_air_quality`: Calidad del aire
- `get_sun_times`: Horarios de salida y puesta del sol
- `get_clothing_advice`: Consejos de vestimenta según el clima
- `get_weekly_summary`: Resumen semanal del clima
- `get_next_rain_day`: Próximo día de lluvia

#### **Google Tasks** (7 herramientas)
- `create_task`: Crear nuevas tareas
- `list_tasks`: Listar tareas existentes
- `complete_task`: Marcar tareas como completadas
- `delete_task`: Eliminar tareas
- `edit_task`: Editar tareas existentes
- `search_tasks`: Buscar tareas específicas
- `add_subtask`: Agregar subtareas

#### **Google Drive** (6 herramientas)
- `search_files`: Buscar archivos en Drive
- `get_file_metadata`: Obtener metadatos de archivos
- `download_file`: Descargar archivos
- `upload_file`: Subir archivos
- `move_file`: Mover archivos entre carpetas
- `delete_file`: Eliminar archivos

#### **Gmail** (6 herramientas)
- `list_messages`: Listar mensajes de correo
- `get_message`: Obtener contenido de mensajes
- `send_message`: Enviar correos electrónicos
- `reply_message`: Responder mensajes
- `delete_message`: Eliminar mensajes
- `modify_labels`: Gestionar etiquetas de correo

#### **Google Calendar** (7 herramientas)
- `list_calendars`: Listar calendarios disponibles
- `list_events`: Listar eventos de un calendario
- `get_event`: Obtener detalles de un evento
- `create_event`: Crear nuevos eventos
- `update_event`: Actualizar eventos existentes
- `delete_event`: Eliminar eventos
- `search_events`: Buscar eventos específicos

## 🏗️ Arquitectura del Sistema

### 1. **Arquitectura General**
```
Usuario → LangGraph Graph → Planner → Executor → Replanner → Respuesta
                ↓
            Memoria Conversacional
```

### 2. **Componentes Principales**

#### **Graph Manager** (`bot/graph.py`)
- Coordina el flujo entre planificador, ejecutor y re-planificador
- Maneja el estado de la conversación
- Detecta bucles y errores automáticamente

#### **Planner** (`bot/planner.py`)
- Analiza la consulta del usuario
- Genera un plan estructurado de pasos
- Considera el contexto de conversación previa

#### **Sistema de Ejecutores Especializados** (`bot/executors/`)
- **Router** (`router.py`): Decide qué ejecutor usar
- **Weather Executor**: Maneja tareas meteorológicas
- **Tasks Executor**: Gestiona Google Tasks
- **Drive Executor**: Opera con Google Drive
- **Gmail Executor**: Maneja correo electrónico
- **Calendar Executor**: Gestiona Google Calendar

#### **Memoria** (`bot/memory.py`)
- Almacena historial de conversaciones
- Mantiene contexto entre sesiones
- Permite recuperar conversaciones anteriores

#### **Herramientas** (`bot/tools/`)
- Implementaciones específicas para cada servicio
- Integración con APIs de Google y servicios externos
- Manejo de autenticación y permisos

### 3. **Flujo de Ejecución**
1. **Entrada**: Usuario envía consulta
2. **Planificación**: Se genera un plan estructurado
3. **Ejecución**: Se ejecutan los pasos usando ejecutores especializados
4. **Re-planificación**: Si es necesario, se adapta el plan
5. **Respuesta**: Se genera respuesta final considerando el contexto

## 🔧 Configuración del Entorno

### Variables de Entorno Requeridas

Crea un archivo `.env` en la raíz del proyecto:

```bash
# ===== AZURE OPENAI (REQUERIDO) =====
AZURE_OPENAI_API_KEY=tu_clave_azure_openai
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Opcional: deployments separados
# AZURE_OPENAI_PLANNER_DEPLOYMENT=gpt-4o-mini
# AZURE_OPENAI_EXECUTOR_DEPLOYMENT=gpt-4o-mini

# ===== CONFIGURACIÓN DE TEMPERATURA =====
PLANNER_TEMPERATURE=0.0
EXECUTOR_TEMPERATURE=0.2
MAX_TOKENS=4000

# ===== TWILIO (PARA WHATSAPP) =====
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=sandbox

# ===== CONFIGURACIÓN DEL SERVIDOR =====
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# ===== LANGGRAPH =====
LANGGRAPH_URL=http://localhost:2024
LANGGRAPH_ASSISTANT_ID=agent
```

### Configuración de Google APIs

Para usar las herramientas de Google (Tasks, Drive, Gmail, Calendar):

1. **Crear proyecto en Google Cloud Console**
2. **Habilitar APIs necesarias**:
   - Google Tasks API
   - Google Drive API
   - Gmail API
   - Google Calendar API
3. **Crear credenciales OAuth 2.0**
4. **Descargar `credentials.json`** y colocarlo en la raíz del proyecto

## 🚀 Instrucciones de Instalación y Uso

### 1. **Instalación de Dependencias**

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd TPFinal-NLP

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Configuración Inicial**

```bash
# Crear archivo .env con las variables requeridas
cp .env.example .env  # Si existe un ejemplo
# Editar .env con tus credenciales

# Verificar configuración de Azure OpenAI
python test/test_azure_config.py
```

**Configuración de LangGraph:**
El archivo `langgraph.json` ya está configurado en la raíz del proyecto:

```json
{
  "dependencies": ["."],
  "graphs": {
    "plan_execute_bot": {
      "path": "plan_and_execute_bot.bot.graph:build_chatbot_graph",
      "description": "🤖 Bot de Planificación y Ejecución\n\n🧠 Planner → ⚡ Executor (26 tools) → 🔄 Replanner\n\nHerramientas disponibles:\n🌤️ Weather (3) | 📋 Google Tasks (6) | 📁 Drive (6)\n📧 Gmail (6) | 📅 Calendar (7)\n\nCon memoria conversacional y re-planificación automática",
      "title": "Plan & Execute Bot con 26 Herramientas",
      "metadata": {
        "visualization": {
          "show_tools": true,
          "theme": "modern",
          "layout": "hierarchical"
        }
      }
    }
  },
  "env": ".env"
}
```

Este archivo le dice a LangGraph Studio:
- Dónde encontrar el grafo del bot
- Cómo visualizarlo
- Qué archivo de entorno usar

### 3. **Modos de Ejecución**

#### **A. Modo CLI (Terminal)**

```bash
# Ejecutar bot en modo CLI
cd plan_and_execute_bot
python main.py

# O directamente
python -m bot.cli
```

**Comandos disponibles en CLI:**
- `/nueva`: Iniciar nueva conversación
- `/historial`: Ver historial de la conversación actual
- `/sesiones`: Listar todas las sesiones guardadas
- `salir` o `exit`: Terminar la sesión

#### **B. Modo LangGraph Studio**

```bash
# Instalar LangGraph CLI si no está instalado
pip install langgraph-cli

# Navegar al directorio del proyecto
cd plan_and_execute_bot

# Iniciar LangGraph Studio
langgraph dev

# Abrir en navegador: http://localhost:2024
```

**Configuración en LangGraph Studio:**
- El grafo `plan_execute_bot` estará disponible automáticamente
- Puedes ver el flujo de ejecución en tiempo real
- Interactúa con el bot usando la interfaz web

**Características de LangGraph Studio:**
- **Visualización del Grafo**: Ve la estructura completa del bot
- **Debugging en Tiempo Real**: Observa cada paso de la ejecución
- **Estado de la Conversación**: Monitorea el estado en cada nodo
- **Historial de Ejecuciones**: Revisa conversaciones anteriores
- **Configuración de Parámetros**: Ajusta temperatura, tokens, etc.

**Uso en LangGraph Studio:**
1. **Seleccionar el Grafo**: Elige `plan_execute_bot` de la lista
2. **Configurar Variables**: Ajusta parámetros si es necesario
3. **Enviar Mensaje**: Escribe tu consulta en el chat
4. **Observar Ejecución**: Ve cómo el bot planifica y ejecuta
5. **Revisar Resultados**: Analiza la respuesta y el proceso

**Comandos Útiles de LangGraph CLI:**
```bash
# Verificar configuración
langgraph dev --help

# Ejecutar en puerto específico
langgraph dev

# Ejecutar con configuración específica
langgraph dev --config langgraph.json

# Ver logs detallados
langgraph dev --log-level debug
```

**Ventajas de LangGraph Studio para Desarrollo:**
- **Debugging Visual**: Ve exactamente qué está pasando en cada paso
- **Análisis de Rendimiento**: Identifica cuellos de botella en la ejecución
- **Testing Interactivo**: Prueba diferentes consultas fácilmente
- **Optimización de Prompts**: Ajusta prompts en tiempo real
- **Documentación Automática**: Genera documentación del flujo
- **Colaboración**: Comparte el grafo con otros desarrolladores

#### **C. Modo Servidor WhatsApp**

```bash
# Iniciar servidor WhatsApp
cd plan_and_execute_bot
python start_server.py

# El servidor estará disponible en http://localhost:8000
```

#### **D. Configuración con ngrok (para WhatsApp)**

```bash
# Instalar ngrok
# Descargar desde https://ngrok.com/

# Exponer el servidor local
ngrok http 8000

# Copiar la URL HTTPS generada (ej: https://abc123.ngrok.io)
```

**Configuración en Twilio:**
1. Ir a [Twilio Console](https://console.twilio.com/)
2. Navegar a **Messaging > Settings > WhatsApp sandbox**
3. En **Webhook URL**, pegar: `https://abc123.ngrok.io/whatsapp`
4. Guardar configuración

### 4. **Testing y Verificación**

```bash
# Probar configuración básica
python test/test_azure_config.py

# Probar bot completo
python test/test_bot.py

# Probar ejecutores especializados
python test/test_specialized_executors.py

# Probar memoria
python test/test_memory.py
```

## 📱 Uso del Bot

### **Ejemplos de Consultas**

#### **Clima y Meteorología**
```
"¿Cuál es el clima en Madrid?"
"¿Necesito paraguas mañana en Barcelona?"
"¿Cuál es la calidad del aire en mi ciudad?"
"¿Cuándo sale el sol hoy?"
```

#### **Google Tasks**
```
"Crear una tarea llamada 'Reunión con cliente' para mañana"
"Listar todas mis tareas pendientes"
"Completar la tarea 'Comprar leche'"
"Buscar tareas que contengan 'proyecto'"
```

#### **Google Drive**
```
"Buscar archivos PDF en mi Drive"
"Subir el archivo 'documento.pdf' a Drive"
"Mover 'presentacion.pptx' a la carpeta 'Trabajo'"
"Descargar el archivo 'reporte.xlsx'"
```

#### **Gmail**
```
"Listar los últimos 10 correos recibidos"
"Enviar un correo a juan@email.com con asunto 'Reunión'"
"Responder al último correo de maria@email.com"
"Buscar correos con la palabra 'proyecto'"
```

#### **Google Calendar**
```
"Crear un evento 'Reunión de equipo' mañana a las 10:00"
"Listar eventos de esta semana"
"Buscar eventos con 'cliente' en el título"
"Actualizar el evento 'Cita médica' para el viernes"
```

## 🔍 Características Avanzadas

### **Memoria Conversacional**
- El bot recuerda conversaciones anteriores
- Mantiene contexto entre sesiones
- Permite referencias a conversaciones previas

### **Re-planificación Inteligente**
- Detecta cuando un plan no funciona
- Adapta automáticamente la estrategia
- Evita bucles infinitos

### **Ejecutores Especializados**
- Cada dominio tiene su propio ejecutor
- Prompts optimizados para cada tarea
- Mejor comprensión y ejecución de comandos

### **Manejo de Errores**
- Validación de configuración al inicio
- Manejo graceful de errores de API
- Respuestas informativas en caso de fallo

## 🛠️ Desarrollo y Extensión

### **Agregar Nuevas Herramientas**

1. **Crear herramienta** en `bot/tools/`
2. **Agregar al ejecutor apropiado** en `bot/executors/`
3. **Actualizar router** en `bot/executors/router.py`
4. **Probar** con `test/test_specialized_executors.py`

### **Agregar Nuevos Ejecutores**

1. **Crear ejecutor** en `bot/executors/`
2. **Actualizar router** para incluir el nuevo dominio
3. **Agregar herramientas** correspondientes
4. **Documentar** en `bot/executors/README.md`

### **Modificar Prompts**

Los prompts están en `bot/prompts.py` y se pueden personalizar según necesidades específicas.

## 📚 Recursos Adicionales

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Google APIs Documentation](https://developers.google.com/)

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad
3. Commit cambios
4. Push a la rama
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

**¡Disfruta usando tu bot inteligente! 🤖✨**
