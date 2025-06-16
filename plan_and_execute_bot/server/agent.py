import logging
import hashlib
import sys
import os

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
            
            # Process with the chatbot
            result_state = await self.chatbot.ainvoke(state)
            
            # Extract response
            response = result_state.get("response", "No pude generar una respuesta.")
            
            # Add bot response to memory
            memory.add_message(session_id, "assistant", response)
            
            LOGGER.info(f"Generated response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Ocurrió un error al procesar tu mensaje: {str(e)}"
            LOGGER.error(f"Error during invoke: {str(e)}", exc_info=True)
            
            # Add error to memory
            try:
                memory.add_message(session_id, "assistant", error_msg)
            except:
                pass  # Don't fail if memory fails
            
            return error_msg
    