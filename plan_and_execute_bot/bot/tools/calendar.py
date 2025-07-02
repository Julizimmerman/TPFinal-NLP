import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from langchain.tools import tool


# Configuración
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Configurar rutas relativas al directorio raíz del proyecto
_CURRENT_DIR = Path(__file__).parent.parent.parent.parent  # Subir 4 niveles desde bot/tools/calendar.py
CREDS_FILE = str(_CURRENT_DIR / 'credentials.json')
TOKEN_FILE = str(_CURRENT_DIR / 'calendar_token.json')


def get_calendar_service():
    """Obtiene el servicio de Google Calendar con manejo mejorado de errores."""
    try:
        # Verificar si existe el archivo de credenciales
        if not Path(CREDS_FILE).exists():
            raise FileNotFoundError(f"No se encontró el archivo {CREDS_FILE}. Por favor, configura las credenciales de Google Calendar.")
        
        creds = None
        # Cargar credenciales guardadas si existen
        if Path(TOKEN_FILE).exists():
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        # Si no hay creds o no son válidas, ejecutar el flujo de OAuth
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Guardar para próximas ejecuciones
            with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
        # Construir el servicio
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        raise Exception(f"Error al configurar Google Calendar: {str(e)}")


@tool
def list_calendars() -> str:
    """Devuelve los calendarios visibles del usuario.
    
    Returns:
        Lista de calendarios con sus IDs y nombres
    """
    try:
        service = get_calendar_service()
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            return "No se encontraron calendarios."
        
        result = "Calendarios disponibles:\n"
        for calendar in calendars:
            result += f"- {calendar['summary']} (ID: {calendar['id']})\n"
        
        return result.strip()
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al listar calendarios: {str(e)}"


@tool
def list_events(calendar_id: str, time_min: str, time_max: str, query: str = None) -> str:
    """Lista eventos dentro de un rango de fechas.
    
    Args:
        calendar_id: ID del calendario
        time_min: Fecha/hora de inicio en formato ISO (ej: '2024-01-01T00:00:00Z')
        time_max: Fecha/hora de fin en formato ISO (ej: '2024-01-31T23:59:59Z')
        query: Término de búsqueda opcional
        
    Returns:
        Lista de eventos en el rango especificado
    """
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=query,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No se encontraron eventos en el rango especificado{' para la búsqueda: ' + query if query else ''}."
        
        result = f"Eventos encontrados ({len(events)}):\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Sin título')
            result += f"- {summary} ({start}) [ID: {event['id']}]\n"
        
        return result.strip()
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al listar eventos: {str(e)}"


@tool
def get_event(calendar_id: str, event_id: str) -> str:
    """Trae los detalles de un evento concreto.
    
    Args:
        calendar_id: ID del calendario
        event_id: ID del evento
        
    Returns:
        Detalles completos del evento
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        result = f"Detalles del evento:\n"
        result += f"Título: {event.get('summary', 'Sin título')}\n"
        result += f"Descripción: {event.get('description', 'Sin descripción')}\n"
        
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        result += f"Inicio: {start}\n"
        result += f"Fin: {end}\n"
        
        if 'location' in event:
            result += f"Ubicación: {event['location']}\n"
        
        if 'attendees' in event:
            attendees = [attendee['email'] for attendee in event['attendees']]
            result += f"Asistentes: {', '.join(attendees)}\n"
        
        result += f"ID del evento: {event['id']}"
        
        return result
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al obtener el evento: {str(e)}"


@tool
def create_event(calendar_id: str, summary: str, start: str, end: str, 
                attendees: str = None, location: str = None, description: str = None) -> str:
    """Crea un nuevo evento.
    
    Args:
        calendar_id: ID del calendario
        summary: Título del evento
        start: Fecha/hora de inicio en formato ISO
        end: Fecha/hora de fin en formato ISO
        attendees: Emails de asistentes separados por comas (opcional)
        location: Ubicación del evento (opcional)
        description: Descripción del evento (opcional)
        
    Returns:
        Confirmación de la creación del evento
    """
    try:
        service = get_calendar_service()
        
        event_body = {
            'summary': summary,
            'start': {'dateTime': start, 'timeZone': 'America/Argentina/Buenos_Aires'},
            'end': {'dateTime': end, 'timeZone': 'America/Argentina/Buenos_Aires'},
        }
        
        if description:
            event_body['description'] = description
        
        if location:
            event_body['location'] = location
        
        if attendees:
            # Convertir string a lista
            attendees_list = [email.strip() for email in attendees.split(',')]
            event_body['attendees'] = [{'email': email} for email in attendees_list]
        
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        
        return f"Evento creado exitosamente: «{summary}» (ID: {event['id']})"
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al crear el evento: {str(e)}"


@tool
def update_event(calendar_id: str, event_id: str, summary: str = None, start: str = None, 
                end: str = None, description: str = None, location: str = None, 
                attendees: str = None) -> str:
    """Modifica campos de un evento existente.
    
    Args:
        calendar_id: ID del calendario
        event_id: ID del evento
        summary: Nuevo título del evento (opcional)
        start: Nueva fecha/hora de inicio en formato ISO (opcional)
        end: Nueva fecha/hora de fin en formato ISO (opcional)
        description: Nueva descripción del evento (opcional)
        location: Nueva ubicación del evento (opcional)
        attendees: Nueva lista de emails de asistentes separados por comas (opcional)
        
    Returns:
        Confirmación de la actualización del evento
    """
    try:
        service = get_calendar_service()
        
        # Obtener el evento actual
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Aplicar los cambios solo si se proporcionan
        if summary is not None:
            event['summary'] = summary
        
        if start is not None:
            event['start'] = {'dateTime': start, 'timeZone': 'America/Argentina/Buenos_Aires'}
        
        if end is not None:
            event['end'] = {'dateTime': end, 'timeZone': 'America/Argentina/Buenos_Aires'}
        
        if description is not None:
            event['description'] = description
        
        if location is not None:
            event['location'] = location
        
        if attendees is not None:
            # Convertir string a lista
            attendees_list = [email.strip() for email in attendees.split(',')]
            event['attendees'] = [{'email': email} for email in attendees_list]
        
        # Actualizar el evento
        updated_event = service.events().update(
            calendarId=calendar_id, 
            eventId=event_id, 
            body=event
        ).execute()
        
        return f"Evento actualizado exitosamente: «{updated_event.get('summary', 'Sin título')}»"
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al actualizar el evento: {str(e)}"


@tool
def delete_event(calendar_id: str, event_id: str) -> str:
    """Elimina o cancela un evento.
    
    Args:
        calendar_id: ID del calendario
        event_id: ID del evento
        
    Returns:
        Confirmación de la eliminación del evento
    """
    try:
        service = get_calendar_service()
        
        # Obtener detalles del evento antes de eliminarlo
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event_title = event.get('summary', 'Sin título')
        
        # Eliminar el evento
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        return f"Evento eliminado exitosamente: «{event_title}»"
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al eliminar el evento: {str(e)}"


@tool
def search_events(calendar_id: str, query: str, days_back: int = 30, days_forward: int = 365) -> str:
    """Busca eventos por término de búsqueda en un rango amplio de fechas.
    
    Args:
        calendar_id: ID del calendario
        query: Término de búsqueda (nombre del evento, asistentes, etc.)
        days_back: Días hacia atrás desde hoy (por defecto 30)
        days_forward: Días hacia adelante desde hoy (por defecto 365)
        
    Returns:
        Lista de eventos que coinciden con la búsqueda
    """
    try:
        from datetime import datetime, timedelta, timezone
        
        # Calcular fechas de búsqueda
        now = datetime.now(timezone(timedelta(hours=-3)))  # Argentina timezone
        time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
        time_max = (now + timedelta(days=days_forward)).isoformat() + 'Z'
        
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=query,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No se encontraron eventos con '{query}' en el rango de búsqueda (desde hace {days_back} días hasta {days_forward} días en el futuro)."
        
        result = f"Eventos encontrados con '{query}' ({len(events)}):\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Sin título')
            result += f"- {summary} ({start}) [ID: {event['id']}]\n"
        
        return result.strip()
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al buscar eventos: {str(e)}"
