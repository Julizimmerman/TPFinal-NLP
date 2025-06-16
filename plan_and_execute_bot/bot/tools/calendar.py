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
                attendees: List[str] = None, location: str = None, description: str = None) -> str:
    """Crea un nuevo evento.
    
    Args:
        calendar_id: ID del calendario
        summary: Título del evento
        start: Fecha/hora de inicio en formato ISO
        end: Fecha/hora de fin en formato ISO
        attendees: Lista de emails de asistentes (opcional)
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
            event_body['attendees'] = [{'email': email} for email in attendees]
        
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        
        return f"Evento creado exitosamente: «{summary}» (ID: {event['id']})"
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al crear el evento: {str(e)}"


@tool
def update_event(calendar_id: str, event_id: str, patch: Dict[str, Any]) -> str:
    """Modifica campos de un evento existente.
    
    Args:
        calendar_id: ID del calendario
        event_id: ID del evento
        patch: Diccionario con los campos a actualizar
        
    Returns:
        Confirmación de la actualización del evento
    """
    try:
        service = get_calendar_service()
        
        # Obtener el evento actual
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Aplicar los cambios del patch
        for key, value in patch.items():
            if key in ['start', 'end'] and isinstance(value, str):
                # Manejar fechas especialmente
                event[key] = {'dateTime': value, 'timeZone': 'America/Argentina/Buenos_Aires'}
            elif key == 'attendees' and isinstance(value, list):
                # Manejar asistentes
                event[key] = [{'email': email} for email in value]
            else:
                event[key] = value
        
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
def find_free_slot(participants: List[str], duration_minutes: int, 
                  time_min: str = None, time_max: str = None) -> str:
    """Devuelve franjas libres comunes entre varios participantes.
    
    Args:
        participants: Lista de emails de participantes
        duration_minutes: Duración requerida en minutos
        time_min: Inicio del rango de búsqueda (opcional, por defecto hoy)
        time_max: Fin del rango de búsqueda (opcional, por defecto en 7 días)
        
    Returns:
        Lista de franjas horarias libres
    """
    try:
        service = get_calendar_service()
        
        # Configurar rango de tiempo por defecto si no se proporciona
        if not time_min:
            time_min = datetime.now().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.now() + timedelta(days=7)).isoformat() + 'Z'
        
        # Consultar disponibilidad
        body = {
            'timeMin': time_min,
            'timeMax': time_max,
            'items': [{'id': email} for email in participants]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        calendars = freebusy_result.get('calendars', {})
        
        # Recopilar todos los períodos ocupados
        busy_periods = []
        for email, calendar_info in calendars.items():
            busy_periods.extend(calendar_info.get('busy', []))
        
        # Ordenar períodos ocupados por tiempo de inicio
        busy_periods.sort(key=lambda x: x['start'])
        
        # Encontrar franjas libres
        free_slots = []
        current_time = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        
        for busy_period in busy_periods:
            busy_start = datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
            
            # Si hay tiempo libre antes del período ocupado
            if (busy_start - current_time).total_seconds() >= duration_minutes * 60:
                free_slots.append({
                    'start': current_time.isoformat(),
                    'end': busy_start.isoformat()
                })
            
            busy_end = datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))
            current_time = max(current_time, busy_end)
        
        # Verificar si hay tiempo libre al final
        if (end_time - current_time).total_seconds() >= duration_minutes * 60:
            free_slots.append({
                'start': current_time.isoformat(),
                'end': end_time.isoformat()
            })
        
        if not free_slots:
            return f"No se encontraron franjas libres de {duration_minutes} minutos para todos los participantes."
        
        result = f"Franjas libres de {duration_minutes} minutos encontradas:\n"
        for slot in free_slots[:10]:  # Limitar a 10 resultados
            start_str = datetime.fromisoformat(slot['start']).strftime('%Y-%m-%d %H:%M')
            end_str = datetime.fromisoformat(slot['end']).strftime('%Y-%m-%d %H:%M')
            result += f"- {start_str} a {end_str}\n"
        
        return result.strip()
    except FileNotFoundError as e:
        return f"❌ Google Calendar no está configurado: {str(e)}"
    except Exception as e:
        return f"❌ Error al buscar franjas libres: {str(e)}"
