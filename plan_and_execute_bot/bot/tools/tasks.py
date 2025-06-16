# tools/tasks.py

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from langchain.tools import tool


# 1) Configuración
SCOPES = ['https://www.googleapis.com/auth/tasks']

# Configurar rutas relativas al directorio raíz del proyecto
_CURRENT_DIR = Path(__file__).parent.parent.parent.parent  # Subir 4 niveles desde bot/tools/tasks.py
CREDS_FILE = str(_CURRENT_DIR / 'credentials.json')
TOKEN_FILE = str(_CURRENT_DIR / 'tasks_token.json')

def get_service():
    """Obtiene el servicio de Google Tasks con manejo mejorado de errores."""
    try:
        # Verificar si existe el archivo de credenciales
        if not Path(CREDS_FILE).exists():
            raise FileNotFoundError(f"No se encontró el archivo {CREDS_FILE}. Por favor, configura las credenciales de Google Tasks siguiendo las instrucciones en CONFIGURACION_TASKS.md")
        
        creds = None
        # 2) Cargar credenciales guardadas si existen
        if Path(TOKEN_FILE).exists():
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        # 3) Si no hay creds o no son válidas, ejecutar el flujo de OAuth
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Guardar para próximas ejecuciones
            with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
        # 4) Construir el servicio
        return build('tasks', 'v1', credentials=creds)
    except Exception as e:
        raise Exception(f"Error al configurar Google Tasks: {str(e)}")

def get_task_id_by_title(title: str) -> str:
    """Función auxiliar para obtener el ID de una tarea por su título."""
    try:
        service = get_service()
        result = service.tasks().list(tasklist='@default').execute()
        for task in result.get("items", []):
            if task["title"].lower() == title.lower():
                return task["id"]
        return None
    except Exception as e:
        return None

@tool
def create_task(title: str) -> str:
    """Crea una nueva tarea en Google Tasks.
    
    Args:
        title: El título de la tarea
        
    Returns:
        Mensaje confirmando la creación de la tarea
    """
    print(f"🔄 [DEBUG] Creating task: {title}")
    try:
        service = get_service()
        existing_id = get_task_id_by_title(title)

        if existing_id:
            # Si existe, crear con un sufijo para evitar duplicados
            original_title = title
            counter = 1
            while existing_id:
                title = f"{original_title} ({counter})"
                existing_id = get_task_id_by_title(title)
                counter += 1

        # Crear nueva tarea
        body = {'title': title}
        task = service.tasks().insert(tasklist='@default', body=body).execute()


        return f"Tarea creada: «{task['title']}» (id: {task['id']})"
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al crear la tarea: {str(e)}"

@tool
def list_tasks() -> str:
    """Lista todas las tareas pendientes en Google Tasks.
    
    Returns:
        Lista de tareas pendientes o mensaje si no hay tareas
    """
    try:
        service = get_service()
        resp = service.tasks().list(tasklist='@default', showCompleted=False).execute()
        items = resp.get('items', [])
        if not items:
            return "No tienes tareas pendientes."
        return "\n".join(f"- {t['title']} (id: {t['id']})" for t in items)
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al listar las tareas: {str(e)}"

@tool
def complete_task(task_title: str) -> str:
    """Marca una tarea como completada.
    
    Args:
        task_title: El título de la tarea a completar
        
    Returns:
        Mensaje confirmando la finalización de la tarea
    """
    try:
        task_id = get_task_id_by_title(task_title)
        if not task_id:
            return f"No se encontró la tarea: «{task_title}»"
        
        service = get_service()
        task = service.tasks().get(tasklist='@default', task=task_id).execute()
        task['status'] = 'completed'
        service.tasks().update(tasklist='@default', task=task_id, body=task).execute()
        return f"Tarea completada: «{task['title']}»"
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al completar la tarea: {str(e)}"

@tool
def delete_task(task_title: str) -> str:
    """Elimina una tarea de Google Tasks.
    
    Args:
        task_title: El título de la tarea a eliminar
        
    Returns:
        Mensaje confirmando la eliminación de la tarea
    """
    try:
        task_id = get_task_id_by_title(task_title)
        if not task_id:
            return f"No se encontró la tarea: «{task_title}»"
        
        service = get_service()
        service.tasks().delete(tasklist='@default', task=task_id).execute()
        return f"Tarea eliminada: «{task_title}» (id: {task_id})"
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al eliminar la tarea: {str(e)}"

@tool
def edit_task(task_title: str, new_title: str = None, new_notes: str = None) -> str:
    """Edita el título o las notas de una tarea existente.
    
    Args:
        task_title: El título actual de la tarea
        new_title: El nuevo título (opcional)
        new_notes: Las nuevas notas (opcional)
        
    Returns:
        Mensaje confirmando la actualización de la tarea
    """
    try:
        task_id = get_task_id_by_title(task_title)
        if not task_id:
            return f"No se encontró la tarea: «{task_title}»"
        if not new_title and not new_notes:
            return "No se especificó un nuevo título o notas."
        
        service = get_service()
        task = service.tasks().get(tasklist='@default', task=task_id).execute()
        if new_title:
            task['title'] = new_title
        if new_notes:
            task['notes'] = new_notes
        updated = service.tasks().update(tasklist='@default', task=task_id, body=task).execute()
        return f"Tarea actualizada: «{updated['title']}»"
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al editar la tarea: {str(e)}"

@tool
def search_tasks(keyword: str) -> str:
    """Busca tareas que contengan una palabra clave en el título.
    
    Args:
        keyword: La palabra clave a buscar en los títulos de las tareas
        
    Returns:
        Lista de tareas que contienen la palabra clave
    """
    try:
        service = get_service()
        tasks = service.tasks().list(tasklist='@default').execute().get("items", [])
        matched = [t for t in tasks if keyword.lower() in t['title'].lower()]

        if not matched:
            return f"No se encontraron tareas que contengan «{keyword}»."

        result = "\n".join(f"- {t['title']} (id: {t['id']})" for t in matched)
        return f"Tareas que contienen «{keyword}»:\n{result}"
    except FileNotFoundError as e:
        return f"❌ Google Tasks no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al buscar tareas: {str(e)}"


