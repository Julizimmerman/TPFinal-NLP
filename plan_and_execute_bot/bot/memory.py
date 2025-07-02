"""Sistema de memoria para el bot conversacional."""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .schemas import ConversationMessage


class ConversationMemory:
    """Gestiona la memoria de conversaciones del bot."""
    
    def __init__(self, memory_file: str = "conversation_memory.json"):
        """Inicializar el sistema de memoria.
        
        Args:
            memory_file: Archivo donde se guardará la memoria
        """
        self.memory_file = memory_file
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.load_memory()
    
    def load_memory(self):
        """Cargar memoria desde archivo."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', {})
                print(f"🧠 [MEMORY] Memoria cargada desde {self.memory_file}")
            except Exception as e:
                print(f"⚠️ [MEMORY] Error cargando memoria: {e}")
                self.sessions = {}
        else:
            print(f"🧠 [MEMORY] Archivo de memoria no existe, iniciando con memoria vacía")
            self.sessions = {}
    
    def save_memory(self):
        """Guardar memoria en archivo."""
        try:
            data = {
                'sessions': self.sessions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"🧠 [MEMORY] Memoria guardada en {self.memory_file}")
        except Exception as e:
            print(f"⚠️ [MEMORY] Error guardando memoria: {e}")
    
    def create_session(self, session_id: str = None) -> str:
        """Crear una nueva sesión de conversación.
        
        Args:
            session_id: ID personalizado para la sesión (usado para WhatsApp)
        
        Returns:
            ID de la sesión
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            print(f"🧠 [MEMORY] Nueva sesión creada: {session_id}")
        else:
            print(f"🧠 [MEMORY] Sesión existente reutilizada: {session_id}")
        
        return session_id
    
    def get_or_create_session(self, session_id: str) -> str:
        """Obtener una sesión existente o crear una nueva.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            ID de la sesión
        """
        return self.create_session(session_id)
    
    def add_message(self, session_id: str, role: str, content: str):
        """Agregar un mensaje al historial de la sesión.
        
        Args:
            session_id: ID de la sesión
            role: 'user' o 'assistant'
            content: Contenido del mensaje
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.sessions[session_id].append(message)
        
        # Mantener solo los últimos 5 mensajes
        if len(self.sessions[session_id]) > 5:
            self.sessions[session_id] = self.sessions[session_id][-5:]
            print(f"🧠 [MEMORY] Historial limitado a 5 mensajes en sesión {session_id[:8]}...")
        
        print(f"🧠 [MEMORY] Mensaje agregado a sesión {session_id[:8]}...")
        
        # Guardar automáticamente después de cada mensaje
        self.save_memory()
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener el historial de conversación de una sesión.
        
        Args:
            session_id: ID de la sesión
            limit: Número máximo de mensajes a retornar (None para todos)
            
        Returns:
            Lista de mensajes de la conversación
        """
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]
        if limit:
            history = history[-limit:]  # Obtener los últimos N mensajes
        
        return history
    
    def get_context_for_planning(self, session_id: str, max_messages: int = 5) -> str:
        """Obtener contexto de conversación para el planificador.
        
        Args:
            session_id: ID de la sesión
            max_messages: Máximo número de mensajes a incluir (por defecto 5)
            
        Returns:
            Contexto formateado para el planificador
        """
        history = self.get_conversation_history(session_id, limit=max_messages)
        
        if not history:
            return "Esta es una nueva conversación."
        
        context_lines = ["Historial de conversación reciente:"]
        for msg in history:
            role_display = "Usuario" if msg['role'] == 'user' else "Asistente"
            context_lines.append(f"{role_display}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def clear_session(self, session_id: str):
        """Limpiar el historial de una sesión específica.
        
        Args:
            session_id: ID de la sesión a limpiar
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_memory()
            print(f"🧠 [MEMORY] Sesión {session_id[:8]}... limpiada")
    
    def list_sessions(self) -> List[str]:
        """Listar todas las sesiones disponibles.
        
        Returns:
            Lista de IDs de sesiones
        """
        return list(self.sessions.keys())
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Obtener resumen de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con información de la sesión
        """
        if session_id not in self.sessions:
            return {}
        
        history = self.sessions[session_id]
        if not history:
            return {'session_id': session_id, 'message_count': 0}
        
        first_message = history[0]
        last_message = history[-1]
        
        return {
            'session_id': session_id,
            'message_count': len(history),
            'first_message_time': first_message['timestamp'],
            'last_message_time': last_message['timestamp'],
            'first_user_message': next((msg['content'] for msg in history if msg['role'] == 'user'), None)
        }


# Instancia global de memoria
memory = ConversationMemory() 