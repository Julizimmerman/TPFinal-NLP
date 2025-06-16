# 📱 Configuración de Twilio WhatsApp Business

Esta guía te ayudará a configurar Twilio WhatsApp Business para integrar tu bot conversacional con WhatsApp.

## 🔧 Requisitos Previos

- Cuenta de Twilio (puedes crear una gratuita en [twilio.com](https://www.twilio.com))
- Un número de teléfono para WhatsApp Business
- Servidor web públicamente accesible (recomendado: ngrok para desarrollo)

## 📋 Paso a Paso

### 1. Crear Cuenta en Twilio

1. Ve a [console.twilio.com](https://console.twilio.com)
2. Regístrate o inicia sesión
3. Verifica tu número de teléfono

### 2. Obtener Credenciales de Twilio

1. En el **Dashboard de Twilio**, busca:
   - **Account SID**: Tu identificador único de cuenta
   - **Auth Token**: Tu token de autenticación (¡mantén esto en secreto!)

2. Copia estas credenciales, las necesitarás para tu archivo `.env`

### 3. Configurar WhatsApp Business

#### Opción A: Usar el Sandbox de Twilio (Desarrollo)
1. Ve a **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Sigue las instrucciones para configurar el sandbox
3. Guarda el número de WhatsApp del sandbox (ejemplo: `whatsapp:+14155238886`)

#### Opción B: Número Real de WhatsApp Business (Producción)
1. Ve a **Messaging** → **Senders** → **WhatsApp senders**
2. Compra un número de teléfono compatible con WhatsApp
3. Completa el proceso de verificación de WhatsApp Business

### 4. Configurar Webhook

1. En la configuración de tu número de WhatsApp:
   - **When a message comes in**: `https://tu-servidor.com/whatsapp`
   - **HTTP Method**: `POST`

2. Para desarrollo local, usa ngrok:
   ```bash
   # Instalar ngrok
   npm install -g ngrok
   
   # Crear túnel a tu servidor local
   ngrok http 8000
   
   # Usar la URL pública generada
   # Ejemplo: https://abc123.ngrok.io/whatsapp
   ```

### 5. Configurar Variables de Entorno

Crea un archivo `.env` con:

```bash
# Credenciales de Twilio
TWILIO_ACCOUNT_SID=tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui

# Número de WhatsApp (incluye 'whatsapp:' al inicio)
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Otras configuraciones...
```

## 🚀 Iniciar el Servidor

1. **Instalar dependencias**:
   ```bash
   cd plan_and_execute_bot
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno**:
   ```bash
   cp env_example.txt .env
   # Edita .env con tus credenciales
   ```

3. **Iniciar LangGraph (en una terminal)**:
   ```bash
   langgraph dev
   ```

4. **Iniciar el servidor WhatsApp (en otra terminal)**:
   ```bash
   python start_server.py
   ```

## 🧪 Probar la Integración

1. **Verificar que el servidor esté funcionando**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Enviar mensaje de prueba**:
   - Si usas el sandbox, envía un mensaje al número de Twilio desde WhatsApp
   - El bot debería responder procesando tu mensaje

## 📝 Logs y Debug

- Los logs del servidor aparecen en la consola
- Para más detalle, activa el modo debug en `.env`:
  ```bash
  DEBUG=true
  LOG_LEVEL=DEBUG
  ```

## ⚠️ Troubleshooting

### Error: "Twilio credentials are missing"
- Verifica que `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` estén en tu `.env`
- Asegúrate de que no haya espacios extra en las credenciales

### Error: "Invalid Twilio signature"
- Verifica que la URL del webhook esté correcta
- Asegúrate de que tu servidor sea accesible públicamente

### No recibo respuestas del bot
- Verifica que LangGraph esté ejecutándose en `http://localhost:8123`
- Revisa los logs del servidor para errores específicos

### Problemas con imágenes
- Asegúrate de que tu cuenta de Twilio tenga permisos para descargar media
- Verifica que las credenciales tengan los permisos correctos

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del servidor
2. Verifica la configuración en la consola de Twilio
3. Consulta la [documentación oficial de Twilio](https://www.twilio.com/docs/whatsapp)

## 🎯 Siguientes Pasos

Una vez configurado, puedes:
- Personalizar las respuestas del bot
- Añadir nuevas herramientas
- Implementar autenticación adicional
- Configurar múltiples números de WhatsApp 