# channel.py
import base64, logging, requests
import asyncio
from abc import ABC, abstractmethod

from fastapi import Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from server.agent import Agent
from server.config import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_WHATSAPP_NUMBER

LOGGER = logging.getLogger("whatsapp")


def twilio_url_to_data_uri(url: str, content_type: str = None) -> str:
    """Download the Twilio media URL and convert to data‑URI (base64)."""
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise RuntimeError("Twilio credentials are missing")

    LOGGER.info(f"Downloading image from Twilio URL: {url}")
    resp = requests.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=20)
    resp.raise_for_status()

    # Use provided content_type or get from headers
    mime = content_type or resp.headers.get('Content-Type')

    # Ensure we have a proper image mime type
    if not mime or not mime.startswith('image/'):
        LOGGER.warning(f"Converting non-image MIME type '{mime}' to 'image/jpeg'")
        mime = "image/jpeg"  # Default to jpeg if not an image type

    b64 = base64.b64encode(resp.content).decode()
    data_uri = f"data:{mime};base64,{b64}"

    return data_uri

class WhatsAppAgent(ABC):
    @abstractmethod
    async def handle_message(self, request: Request) -> str: ...

class WhatsAppAgentTwilio(WhatsAppAgent):
    def __init__(self) -> None:
        if not (TWILIO_AUTH_TOKEN and TWILIO_ACCOUNT_SID):
            raise ValueError("Twilio credentials are not configured")
        self.agent = Agent()
        # Inicializar cliente de Twilio para envío de mensajes
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    def _clean_whatsapp_text(self, text: str) -> str:
        """Limpia el texto para que sea compatible con WhatsApp/Twilio."""
        import re
        
        # Remover markdown bold (**texto**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remover markdown italic (*texto*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Limpiar caracteres problemáticos para XML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Normalizar saltos de línea
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()

    async def send_whatsapp_message(self, to_number: str, message: str):
        """Envía un mensaje de WhatsApp usando la API REST de Twilio."""
        try:
            # Limpiar el texto antes de enviarlo
            clean_message = self._clean_whatsapp_text(message)
            
            # Limitar la longitud de la respuesta para WhatsApp
            if len(clean_message) > 1600:  # WhatsApp tiene límite de caracteres
                clean_message = clean_message[:1600] + "..."
                LOGGER.warning("Respuesta truncada por límite de WhatsApp")
            
            # Determinar el número de origen
            from_number = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}" if TWILIO_WHATSAPP_NUMBER != "sandbox" else "whatsapp:+14155238886"
            
            # Enviar mensaje usando la API de Twilio
            message_instance = self.twilio_client.messages.create(
                body=clean_message,
                from_=from_number,
                to=to_number
            )
            
            LOGGER.info(f"✅ Mensaje enviado exitosamente. SID: {message_instance.sid}")
            LOGGER.info(f"📱 De: {from_number} → Para: {to_number}")
            LOGGER.info(f"📝 Contenido: {clean_message[:100]}{'...' if len(clean_message) > 100 else ''}")
            
        except Exception as e:
            LOGGER.error(f"❌ Error enviando mensaje de WhatsApp: {e}")
            raise

    async def handle_message_async(self, form_data: dict):
        """Maneja mensajes de WhatsApp de forma asíncrona y envía respuesta usando API de Twilio."""
        try:
            sender = form_data.get("From", "").strip()
            content = form_data.get("Body", "").strip()
            
            if not sender:
                LOGGER.error("Missing 'From' in request form")
                return

            LOGGER.info(f"📱 Procesando mensaje de {sender}: {content[:50]}{'...' if len(content) > 50 else ''}")

            # Collect ALL images (you'll forward only the first one for now)
            images = []
            num_media = int(form_data.get("NumMedia", "0"))
            for i in range(num_media):
                url = form_data.get(f"MediaUrl{i}", "")
                ctype = form_data.get(f"MediaContentType{i}", "")
                if url and ctype.startswith("image/"):
                    try:
                        images.append({
                            "url": url,
                            "data_uri": twilio_url_to_data_uri(url, ctype),
                        })
                    except Exception as err:
                        LOGGER.error("Failed to download %s: %s", url, err)

            # Assemble payload for the LangGraph agent
            input_data = {
                "id": sender,
                "user_message": content,
            }
            if images:
                # Pass all images to the agent
                input_data["images"] = [
                    {"image_url": {"url": img["data_uri"]}} for img in images
                ]

            # Procesar mensaje con el agente con manejo robusto de errores
            reply = None
            try:
                LOGGER.info("🤖 Procesando mensaje con el agente...")
                reply = await self.agent.invoke(**input_data)
                LOGGER.info("✅ Agente procesó el mensaje exitosamente")
            except Exception as e:
                LOGGER.error(f"❌ Error crítico en el agente: {e}", exc_info=True)
                # Respuesta de emergencia si todo lo demás falla
                reply = "Lo siento, estoy experimentando dificultades técnicas. Por favor, inténtalo de nuevo en unos momentos."
            
            # Asegurar que tenemos una respuesta válida
            if not reply or not isinstance(reply, str) or not reply.strip():
                LOGGER.warning("El agente no devolvió una respuesta válida")
                reply = "Disculpa, no pude procesar tu mensaje. Por favor, inténtalo de nuevo."
            
            # Enviar la respuesta usando la API de Twilio
            await self.send_whatsapp_message(sender, reply)
            
        except Exception as e:
            LOGGER.exception(f"❌ Error crítico en handle_message_async: {e}")
            # Intentar enviar mensaje de error
            try:
                if 'sender' in locals() and sender:
                    await self.send_whatsapp_message(
                        sender, 
                        "Lo siento, ocurrió un error inesperado. Por favor, inténtalo de nuevo."
                    )
            except:
                LOGGER.error("No se pudo enviar mensaje de error")

    async def handle_message(self, request: Request) -> str:
        form = await request.form()

        sender  = form.get("From", "").strip()
        content = form.get("Body", "").strip()
        if not sender:
            raise HTTPException(400, detail="Missing 'From' in request form")

        # Collect ALL images (you'll forward only the first one for now)
        images = []
        for i in range(int(form.get("NumMedia", "0"))):
            url   = form.get(f"MediaUrl{i}", "")
            ctype = form.get(f"MediaContentType{i}", "")
            if url and ctype.startswith("image/"):
                try:
                    images.append({
                        "url": url,
                        "data_uri": twilio_url_to_data_uri(url, ctype),
                    })
                except Exception as err:
                    LOGGER.error("Failed to download %s: %s", url, err)

        # Assemble payload for the LangGraph agent
        input_data = {
            "id": sender,
            "user_message": content,
        }
        if images:
            # Pass all images to the agent
            input_data["images"] = [
                {"image_url": {"url": img["data_uri"]}} for img in images
            ]

        # Procesar mensaje con el agente con manejo robusto de errores
        reply = None
        try:
            reply = await self.agent.invoke(**input_data)
        except Exception as e:
            LOGGER.error(f"❌ Error crítico en el agente: {e}", exc_info=True)
            # Respuesta de emergencia si todo lo demás falla
            reply = "Lo siento, estoy experimentando dificultades técnicas. Por favor, inténtalo de nuevo en unos momentos."
        
        # Asegurar que tenemos una respuesta válida
        if not reply or not isinstance(reply, str) or not reply.strip():
            LOGGER.warning("El agente no devolvió una respuesta válida")
            reply = "Disculpa, no pude procesar tu mensaje. Por favor, inténtalo de nuevo."
        
        # Limpiar markdown que puede causar problemas en WhatsApp
        reply = self._clean_whatsapp_text(reply)
        
        # Limitar la longitud de la respuesta para WhatsApp
        if len(reply) > 1600:  # WhatsApp tiene límite de caracteres
            reply = reply[:1600] + "..."
            LOGGER.warning("Respuesta truncada por límite de WhatsApp")

        # Crear respuesta TwiML
        twiml = MessagingResponse()
        twiml.message(reply)
        
        twiml_str = str(twiml)
        LOGGER.info(f"Enviando respuesta de {len(reply)} caracteres")
        LOGGER.info(f"TwiML generado: {twiml_str}")
        return twiml_str
