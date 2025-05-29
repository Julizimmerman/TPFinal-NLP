# Configuración de Google Tasks API

Este documento explica cómo configurar las herramientas de Google Tasks para el bot ejecutor.

## Herramientas Disponibles

El bot ahora incluye las siguientes herramientas para gestionar tareas en Google Tasks:

- **`create_task`**: Crea una nueva tarea con título y notas opcionales
- **`list_tasks`**: Lista todas las tareas pendientes
- **`complete_task`**: Marca una tarea como completada
- **`delete_task`**: Elimina una tarea
- **`edit_task`**: Edita el título o notas de una tarea existente
- **`search_tasks`**: Busca tareas que contengan una palabra clave

## Configuración Inicial

### 1. Crear un Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Tasks:
   - Ve a "APIs & Services" > "Library"
   - Busca "Google Tasks API"
   - Haz clic en "Enable"

### 2. Configurar OAuth 2.0

1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "OAuth client ID"
3. Si es la primera vez, configura la pantalla de consentimiento OAuth:
   - Selecciona "External" (a menos que tengas Google Workspace)
   - Completa la información requerida
   - Agrega tu email en "Test users"
4. Para el OAuth client ID:
   - Tipo de aplicación: "Desktop application"
   - Nombre: "Plan and Execute Bot"
5. Descarga el archivo JSON de credenciales

### 3. Configurar el Archivo de Credenciales

1. Renombra el archivo descargado a `credentials.json`
2. Colócalo en el directorio raíz del proyecto `plan_and_execute_bot/`
3. El archivo debe tener una estructura similar a:

```json
{
  "installed": {
    "client_id": "tu-client-id.googleusercontent.com",
    "project_id": "tu-proyecto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "tu-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 4. Instalar Dependencias

Ejecuta el siguiente comando para instalar las dependencias de Google API:

```bash
pip install -r requirements.txt
```

### 5. Primera Autenticación

La primera vez que uses las herramientas de tareas:

1. El bot abrirá automáticamente tu navegador
2. Inicia sesión con tu cuenta de Google
3. Autoriza el acceso a Google Tasks
4. Se creará automáticamente un archivo `token.json` para futuras autenticaciones

## Uso de las Herramientas

### Ejemplos de Comandos

- **Crear tarea**: "Crea una tarea llamada 'Comprar leche'"
- **Listar tareas**: "Muéstrame mis tareas pendientes"
- **Completar tarea**: "Marca como completada la tarea 'Comprar leche'"
- **Buscar tareas**: "Busca tareas que contengan 'reunión'"
- **Editar tarea**: "Cambia el título de la tarea 'Comprar leche' a 'Comprar leche y pan'"
- **Eliminar tarea**: "Elimina la tarea 'Comprar leche'"

### Manejo de Duplicados

Si intentas crear una tarea con un título que ya existe, el sistema automáticamente agregará un sufijo numérico para evitar duplicados (ej: "Mi tarea (1)", "Mi tarea (2)").

## Solución de Problemas

### Error de Credenciales

Si obtienes errores relacionados con credenciales:

1. Verifica que `credentials.json` esté en el directorio correcto
2. Asegúrate de que la API de Google Tasks esté habilitada
3. Elimina `token.json` y vuelve a autenticarte

### Error de Permisos

Si obtienes errores de permisos:

1. Verifica que tu email esté en la lista de "Test users" en la configuración OAuth
2. Asegúrate de estar usando la cuenta correcta de Google

### Problemas de Red

Las herramientas requieren conexión a internet para funcionar. Si hay problemas de conectividad, las herramientas devolverán mensajes de error descriptivos.

## Archivos Importantes

- `credentials.json`: Credenciales OAuth (no incluir en control de versiones)
- `token.json`: Token de acceso (se genera automáticamente)
- `plan_and_execute_bot/bot/tools/tasks.py`: Implementación de las herramientas 