# 🔐 Configuración de Credenciales - Guía Completa

Esta guía te ayuda a organizar todas las credenciales necesarias para que el bot funcione correctamente.

## 📁 **Estructura de Archivos de Credenciales**

Todos los archivos de credenciales deben estar en la **raíz del proyecto** (`TPFinal-NLP/`):

```
TPFinal-NLP/
├── credentials.json          # ✅ Credenciales de Google APIs (compartido)
├── gmail_token.json         # 🔄 Token de Gmail (se genera automáticamente)
├── calendar_token.json      # 🔄 Token de Calendar (se genera automáticamente)
├── tasks_token.json         # 🔄 Token de Tasks (se genera automáticamente)
├── drive_token.json         # 🔄 Token de Drive (se genera automáticamente)
├── conversation_memory.json # 🧠 Memoria del bot (se genera automáticamente)
├── .env                     # ⚙️ Variables de entorno (Twilio, Azure, etc.)
└── plan_and_execute_bot/    # 📂 Código del bot
```

## 🔑 **Archivos de Credenciales Necesarios**

### 1. **credentials.json** (OBLIGATORIO)
- **Qué es**: Credenciales de Google Cloud para todas las APIs
- **Cómo obtenerlo**: 
  1. Ve a [Google Cloud Console](https://console.cloud.google.com)
  2. Crea un proyecto o selecciona uno existente
  3. Habilita las APIs necesarias:
     - Gmail API
     - Google Calendar API  
     - Google Tasks API
     - Google Drive API
  4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente OAuth 2.0"
  5. Tipo de aplicación: "Aplicación de escritorio"
  6. Descarga el archivo JSON y renómbralo a `credentials.json`

### 2. **Archivos de Token** (SE GENERAN AUTOMÁTICAMENTE)
- `gmail_token.json` - Se crea al autorizar Gmail por primera vez
- `calendar_token.json` - Se crea al autorizar Calendar por primera vez  
- `tasks_token.json` - Se crea al autorizar Tasks por primera vez
- `drive_token.json` - Se crea al autorizar Drive por primera vez

### 3. **.env** (OBLIGATORIO para WhatsApp)
```bash
# Credenciales de Azure OpenAI
AZURE_OPENAI_API_KEY=tu_clave_aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Credenciales de Twilio WhatsApp
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token

# Configuración del servidor
DEBUG=false
LOG_LEVEL=INFO
```

## 🔧 **Verificar Configuración Actual**

Para verificar que todo está correctamente ubicado:

```bash
# Desde la raíz del proyecto
ls -la *.json *.env

# Deberías ver:
# -rw-r--r-- calendar_token.json
# -rw-r--r-- credentials.json      ← ESTE ES CRUCIAL
# -rw-r--r-- gmail_token.json
# -rw-r--r-- tasks_token.json
# -rw-r--r-- .env                  ← ESTE TAMBIÉN ES CRUCIAL
```

## 🚀 **Proceso de Autorización Primera Vez**

1. **Coloca `credentials.json`** en la raíz del proyecto
2. **Configura tu `.env`** con las credenciales de Twilio y Azure
3. **Inicia el bot** - te pedirá autorizar cada servicio de Google una por una
4. **Sigue las instrucciones** en el navegador para autorizar cada API
5. **Los tokens se generan automáticamente** y se guardan para futuras ejecuciones

## ⚠️ **Problemas Comunes**

### "No se encontró el archivo credentials.json"
- ✅ **Solución**: Asegúrate de que `credentials.json` esté en la raíz del proyecto
- ✅ **Verificar**: Ejecuta `ls credentials.json` desde la raíz

### "Google Tasks no está configurado"
- ✅ **Solución**: Verifica que hayas habilitado Google Tasks API en Google Cloud Console
- ✅ **Verificar**: El archivo `credentials.json` debe incluir permisos para Tasks API

### "Error al procesar tu mensaje: All connection attempts failed"
- ✅ **Solución**: Problema de conectividad o credenciales de Azure OpenAI
- ✅ **Verificar**: Revisa las variables `AZURE_OPENAI_*` en tu `.env`

### "Twilio credentials are missing"
- ✅ **Solución**: Configura `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` en `.env`
- ✅ **Verificar**: Las credenciales están correctas en tu dashboard de Twilio

## 🔒 **Seguridad**

- ✅ **NUNCA** subas `credentials.json` a Git
- ✅ **NUNCA** subas archivos `*_token.json` a Git  
- ✅ **NUNCA** subas `.env` a Git
- ✅ Todos estos archivos están en `.gitignore`

## 📞 **Soporte**

Si después de seguir esta guía sigues teniendo problemas:

1. **Verifica la estructura de archivos** con `ls -la *.json *.env`
2. **Revisa los logs** del servidor para mensajes de error específicos
3. **Comprueba la configuración** de Google Cloud Console
4. **Valida las credenciales** de Twilio en su dashboard 