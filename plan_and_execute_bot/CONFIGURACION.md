# Configuración de Variables de Entorno para Azure OpenAI

Este proyecto utiliza Azure OpenAI para configurar los modelos de IA y otros parámetros. 

## Archivo .env

Crea un archivo `.env` en la raíz del directorio `plan_and_execute_bot/` con las siguientes variables:

### Variables Requeridas para Azure OpenAI

```bash
# Configuración básica de Azure OpenAI (TODAS REQUERIDAS)
AZURE_OPENAI_API_KEY=tu_clave_azure_openai
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### Variables Opcionales

```bash
# Clave de API de Tavily (opcional)
TAVILY_API_KEY=tu_clave_tavily_aqui

# Deployments separados (opcional - si no se especifican, usa AZURE_OPENAI_DEPLOYMENT para ambos)
AZURE_OPENAI_PLANNER_DEPLOYMENT=gpt-4
AZURE_OPENAI_EXECUTOR_DEPLOYMENT=gpt-35-turbo

# Configuración de temperatura
PLANNER_TEMPERATURE=0.0
EXECUTOR_TEMPERATURE=0.2

# Límite de tokens
MAX_TOKENS=4000

# Modo debug
DEBUG=false
```

## Configuración Simple (Un solo deployment)

Si solo tienes un deployment (como `gpt-4o-mini`), usa esta configuración mínima:

```bash
# Variables requeridas
AZURE_OPENAI_API_KEY=1234567890abcdef1234567890abcdef
AZURE_OPENAI_ENDPOINT=https://mi-recurso-openai.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Variables opcionales (puedes omitir estas)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PLANNER_TEMPERATURE=0.0
EXECUTOR_TEMPERATURE=0.2
MAX_TOKENS=4000
DEBUG=false
```

## Configuración Avanzada (Deployments separados)

Si tienes múltiples deployments y quieres usar diferentes modelos:

```bash
# Variables requeridas
AZURE_OPENAI_API_KEY=1234567890abcdef1234567890abcdef
AZURE_OPENAI_ENDPOINT=https://mi-recurso-openai.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini  # deployment por defecto

# Deployments específicos (opcional)
AZURE_OPENAI_PLANNER_DEPLOYMENT=gpt-4-deployment
AZURE_OPENAI_EXECUTOR_DEPLOYMENT=gpt-35-turbo-deployment

# Otras opciones...
```

## Configuración de Azure OpenAI

Para obtener las variables necesarias:

1. **AZURE_OPENAI_API_KEY**: Ve a tu recurso de Azure OpenAI en el portal de Azure → "Keys and Endpoint" → copia una de las claves
2. **AZURE_OPENAI_ENDPOINT**: En la misma sección, copia el endpoint (debe terminar con `/`)
3. **AZURE_OPENAI_API_VERSION**: Usa `2024-02-15-preview` o la versión más reciente disponible
4. **AZURE_OPENAI_DEPLOYMENT**: Nombre del deployment de tu modelo en Azure (ej: `gpt-4o-mini`)

### Crear Deployment en Azure

En tu recurso de Azure OpenAI:
1. Ve a "Model deployments" 
2. Crea un deployment para tu modelo (ej: GPT-4o-mini)
3. Usa el nombre de este deployment en `AZURE_OPENAI_DEPLOYMENT`

💡 **Nota**: Si solo tienes un deployment, el sistema lo usará automáticamente tanto para planificación como para ejecución.

## Validación

El sistema validará automáticamente que todas las variables requeridas estén presentes al iniciar. Si falta alguna variable requerida, el programa mostrará un error descriptivo y se cerrará.

## Configuración Avanzada

- **AZURE_OPENAI_DEPLOYMENT**: Deployment principal que se usa por defecto
- **AZURE_OPENAI_PLANNER_DEPLOYMENT**: Deployment específico para planificación (opcional)
- **AZURE_OPENAI_EXECUTOR_DEPLOYMENT**: Deployment específico para ejecución (opcional)
- **PLANNER_TEMPERATURE**: Controla la creatividad del planificador (0.0 = determinista, 1.0 = creativo)
- **EXECUTOR_TEMPERATURE**: Controla la creatividad del ejecutor
- **MAX_TOKENS**: Límite máximo de tokens por respuesta
- **DEBUG**: Activa logs adicionales para depuración 