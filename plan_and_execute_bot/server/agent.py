import logging
import hashlib
import sys
import os
import asyncio

# Agregar el directorio del bot al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bot.graph import build_chatbot_graph
from bot.memory import memory

LOGGER = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        """Inicializar el agente usando directamente el grafo del bot."""
        try:
            self.chatbot = build_chatbot_graph()
            LOGGER.info("✅ Chatbot grafo inicializado correctamente")
        except Exception as e:
            LOGGER.error(f"❌ Error inicializando chatbot grafo: {e}")
            raise

    async def invoke(self, id: str, user_message: str, images: list = None) -> str:
        """
        Process a user message through the chatbot graph directly.
        
        Args:
            id: The unique identifier for the conversation (WhatsApp phone number)
            user_message: The message content from the user
            images: List of dictionaries with image data
            
        Returns:
            str: The response message from the bot
        """
        # Create a consistent session ID from the WhatsApp phone number
        session_id = hashlib.md5(id.encode()).hexdigest()
        LOGGER.info(f"Invoking agent with session_id: {session_id} (from WhatsApp ID: {id})")

        try:
            # Ensure session exists in memory
            memory.get_or_create_session(session_id)
            
            # Add user message to memory
            memory.add_message(session_id, "user", user_message)
            
            # TODO: Handle images if needed (for future implementation)
            if images:
                LOGGER.info(f"Received {len(images)} images (image processing not yet implemented)")
            
            # Prepare state for the chatbot
            state = {
                "input": user_message,
                "session_id": session_id,
                "conversation_history": [],
                "past_steps": []
            }
            
            LOGGER.info(f"Processing message with chatbot: '{user_message}'")
            
            # Process with the chatbot with timeout
            try:
                # Agregar timeout para evitar que el grafo se quede colgado
                result_state = await asyncio.wait_for(
                    self.chatbot.ainvoke(state), 
                    timeout=120.0  # 2 minutos máximo
                )
                
                # Extract response
                response = result_state.get("response")
                
                # Verificar que tenemos una respuesta válida
                if not response or not isinstance(response, str) or not response.strip():
                    LOGGER.warning("El grafo no generó una respuesta válida")
                    response = "Disculpa, no pude procesar completamente tu solicitud. ¿Podrías reformular tu pregunta?"
                
                # Add bot response to memory
                memory.add_message(session_id, "assistant", response)
                
                LOGGER.info(f"Generated response: {response}")
                return response
                
            except asyncio.TimeoutError:
                LOGGER.error("El procesamiento del mensaje superó el tiempo límite")
                error_msg = "Disculpa, tu solicitud está tomando demasiado tiempo en procesarse. Por favor, intenta con una consulta más específica."
                memory.add_message(session_id, "assistant", error_msg)
                return error_msg
                
            except Exception as graph_error:
                LOGGER.error(f"Error específico en el grafo: {str(graph_error)}", exc_info=True)
                # Intentar respuesta de emergencia básica
                fallback_msg = self._generate_fallback_response(user_message)
                memory.add_message(session_id, "assistant", fallback_msg)
                return fallback_msg
            
        except Exception as e:
            error_msg = f"Ocurrió un error al procesar tu mensaje. Por favor, inténtalo de nuevo."
            LOGGER.error(f"Error during invoke: {str(e)}", exc_info=True)
            
            # Add error to memory
            try:
                memory.add_message(session_id, "assistant", error_msg)
            except:
                pass  # Don't fail if memory fails
            
            return error_msg
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Genera una respuesta de emergencia cuando el grafo principal falla."""
        user_lower = user_message.lower()
        
        # Respuestas específicas para casos comunes
        if any(word in user_lower for word in ["clima", "weather", "temperatura"]):
            return "No pude obtener la información del clima en este momento. Por favor, inténtalo de nuevo más tarde."
        elif any(word in user_lower for word in ["tarea", "task", "crear", "hacer"]):
            return "No pude acceder a las tareas en este momento. Por favor, inténtalo de nuevo más tarde."
        elif any(word in user_lower for word in ["reunión", "meeting", "calendario", "calendar"]):
            return "No pude acceder al calendario en este momento. Por favor, inténtalo de nuevo más tarde."
        elif any(word in user_lower for word in ["mail", "email", "correo", "enviar"]):
            return "No pude acceder al correo en este momento. Por favor, inténtalo de nuevo más tarde."
        else:
            return "Disculpa, no pude procesar tu solicitud en este momento. Por favor, inténtalo de nuevo o reformula tu pregunta."
    