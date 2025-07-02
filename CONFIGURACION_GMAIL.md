# Configuración de Gmail para el Bot

## Problema Actual
El sistema está fallando porque no tiene las credenciales de Gmail configuradas correctamente. El error "Blocking call to time.sleep" indica que el sistema está intentando abrir un navegador para autenticación OAuth, pero no puede hacerlo en el entorno actual.

## Solución

### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Gmail:
   - Ve a "APIs & Services" > "Library"
   - Busca "Gmail API"
   - Haz clic en "Enable"

### 2. Crear Credenciales OAuth 2.0

1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "OAuth 2.0 Client IDs"
3. Selecciona "Desktop application"
4. Dale un nombre (ej: "Gmail Bot")
5. Haz clic en "Create"
6. Descarga el archivo JSON de credenciales

### 3. Configurar el Archivo de Credenciales

1. Renombra el archivo descargado a `credentials.json`
2. Colócalo en el directorio raíz del proyecto (mismo nivel que `requirements.txt`)
3. El archivo debe estar en: `/Users/Colegio/Documents/4to/1er_Semestre/Repositorios/TPFinal-NLP/credentials.json`

### 4. Estructura de Archivos Requerida

```
TPFinal-NLP/
├── credentials.json          ← REQUERIDO: Archivo de credenciales de Google
├── gmail_token.json          ← Se creará automáticamente después de la primera autenticación
├── requirements.txt
├── plan_and_execute_bot/
└── ...
```

### 5. Primera Ejecución

La primera vez que ejecutes el sistema con Gmail:
1. Se abrirá automáticamente un navegador web
2. Te pedirá que inicies sesión con tu cuenta de Google
3. Te pedirá permisos para acceder a Gmail
4. Después de autorizar, se creará automáticamente el archivo `gmail_token.json`

### 6. Permisos Requeridos

El sistema necesita los siguientes permisos de Gmail:
- **gmail.modify**: Para leer, modificar y gestionar mensajes existentes
- **gmail.send**: Para enviar nuevos mensajes y respuestas  
- **gmail.labels**: Para gestionar etiquetas personalizadas
- `https://www.googleapis.com/auth/gmail.modify` - Para leer, enviar y modificar mensajes
- `https://www.googleapis.com/auth/gmail.send` - Para enviar mensajes
- `https://www.googleapis.com/auth/gmail.labels` - Para gestionar etiquetas

### 7. Verificación

Para verificar que todo funciona:
1. Asegúrate de que `credentials.json` existe en el directorio raíz
2. Ejecuta el servidor: `cd plan_and_execute_bot && python start_server.py`
3. Prueba con una consulta simple: "Listar mis mensajes no leídos"

### 8. Solución Temporal

Si no puedes configurar las credenciales ahora, puedes:

1. **Usar el modo de desarrollo con bloqueo permitido:**
   ```bash
   langgraph dev --allow-blocking
   ```

2. **O configurar la variable de entorno:**
   ```bash
   export BG_JOB_ISOLATED_LOOPS=true
   ```

### 9. Notas Importantes

- El archivo `credentials.json` contiene información sensible, no lo subas a Git
- El archivo `gmail_token.json` se crea automáticamente y contiene los tokens de acceso
- Si cambias de cuenta de Google, elimina `gmail_token.json` para forzar una nueva autenticación

### 10. Troubleshooting

**Error: "No se encontró el archivo credentials.json"**
- Verifica que el archivo existe en el directorio raíz
- Verifica que el nombre es exactamente `credentials.json`

**Error: "Blocking call to time.sleep"**
- Configura las credenciales como se describe arriba
- O usa `langgraph dev --allow-blocking`

**Error de permisos en Gmail**
- Verifica que la API de Gmail esté habilitada en Google Cloud Console
- Verifica que las credenciales OAuth 2.0 estén configuradas correctamente 