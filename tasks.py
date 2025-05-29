# tools/notes_oauth.py

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# 1) Configuración
SCOPES = ['https://www.googleapis.com/auth/tasks']
CREDS_FILE = 'credentials.json'  # tu JSON con "installed":{...}
TOKEN_FILE = 'token.json'        # donde se guardarán los tokens

def get_service():
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

# Ejemplo de wrappers usando get_service()

def create_task(title: str, notes: str = "") -> str:
    service = get_service()
    existing_id = get_task_id_by_title(title)

    if existing_id:
        print(f"Ya existe una tarea con el título: «{title}» (id: {existing_id})")
        choice = input("¿Querés reemplazarla (r), crear otra igual (c), o cambiar el nombre (n)? ").strip().lower()

        if choice == "r":
            # Reemplazar: borrar y crear nueva
            service.tasks().delete(tasklist='@default', task=existing_id).execute()
            print("Tarea anterior eliminada.")
        elif choice == "n":
            new_title = input("Ingresá el nuevo título: ").strip()
            title = new_title
        elif choice != "c":
            return "Operación cancelada por el usuario."

    # Crear nueva tarea
    body = {'title': title}
    task = service.tasks().insert(tasklist='@default', body=body).execute()

    if notes:
        task['notes'] = notes
        service.tasks().update(tasklist='@default', task=task['id'], body=task).execute()

    return f"Tarea creada: «{task['title']}» (id: {task['id']})"

def list_tasks() -> str:
    service = get_service()
    resp = service.tasks().list(tasklist='@default', showCompleted=False).execute()
    items = [t for t in resp.get('items', []) if 'due' not in t]
    if not items:
        return "No tienes notas pendientes."
    return "\n".join(f"- {t['id']}: {t['title']}" for t in items)

def get_task_id_by_title(title: str) -> str:
    service = get_service()
    result = service.tasks().list(tasklist='@default').execute()
    for task in result.get("items", []):
        if task["title"].lower() == title.lower():
            return task["id"]
    return None


def complete_task(task_title: str) -> str:
    task_id = get_task_id_by_title(task_title)
    if not task_id:
        return f"No se encontró la tarea: «{task_title}»"
    service = get_service()
    task = service.tasks().get(tasklist='@default', task=task_id).execute()
    task['status'] = 'completed'
    service.tasks().update(tasklist='@default', task=task_id, body=task).execute()
    return f"Tarea completada: «{task['title']}»"

def delete_task(task_title: str) -> str:
    task_id = get_task_id_by_title(task_title)
    if not task_id:
        return f"No se encontró la tarea: «{task_title}»"
    service = get_service()
    service.tasks().delete(tasklist='@default', task=task_id).execute()
    return f"Tarea eliminada (id: {task_id})"

def edit_task(task_title: str, new_title: str = None, new_notes: str = None) -> str:
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

# def search_tasks(keyword: str) -> str:
#     service = get_service()
#     tasks = service.tasks().list(tasklist='@default').execute().get("items", [])
#     matched = [t for t in tasks if keyword.lower() in t['title'].lower()]
#     return "\n".join(f"- {t['title']} (id: {t['id']})" for t in matched) or "No se encontraron tareas."

def search_tasks(keyword: str) -> str:
    service = get_service()
    tasks = service.tasks().list(tasklist='@default').execute().get("items", [])
    matched = [t for t in tasks if keyword.lower() in t['title'].lower()]

    if not matched:
        return f"No se encontraron tareas que contengan «{keyword}»."

    result = "\n".join(f"- {t['title']} (id: {t['id']})" for t in matched)
    return f"Tareas que contienen «{keyword}»:\n{result}"


if __name__ == "__main__":
    # print(create_task("Mi primera tarea")) 
    # print(list_tasks())
    # print(complete_task("Mi primera tarea")) 
    # print(list_tasks())

    # print(create_task("Tarea para editar"))
    # print(edit_task("Tarea para editar", new_notes = "Notas editadas"))
    # print(list_tasks())

    # print(create_task(title="Tarea con notas", notes="Estas son las notas"))
    # print(list_tasks())

    # print(delete_task("Mi primera tarea"))
    print(create_task("Mi cuarta tarea", None))
    print(search_tasks("primera"))


