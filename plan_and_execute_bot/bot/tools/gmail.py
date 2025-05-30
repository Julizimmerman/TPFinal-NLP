# gmail.py

import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from langchain.tools import tool

# --- CONFIGURACIÓN OAuth ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configurar rutas relativas al directorio del bot
_CURRENT_DIR = Path(__file__).parent.parent.parent  # Subir 3 niveles desde bot/tools/gmail.py
CREDS_FILE = str(_CURRENT_DIR / 'credentials.json')
TOKEN_FILE = str(_CURRENT_DIR / 'gmail_token.json')


def get_gmail_service():
    """Inicializa y devuelve el servicio de Gmail."""
    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


@tool
def list_messages(query: str = None, label_ids: List[str] = None, max_results: int = 10) -> str:
    """Lista hilos o correos según query (label, fecha, etc.).
    
    Args:
        query: Consulta de búsqueda (opcional, ej: "from:ejemplo@gmail.com", "subject:importante")
        label_ids: IDs de etiquetas para filtrar (opcional)
        max_results: Número máximo de resultados (opcional, por defecto 10)
        
    Returns:
        Lista de mensajes que coinciden con los criterios
    """
    try:
        service = get_gmail_service()
        
        # Preparar parámetros de búsqueda
        search_params = {
            'userId': 'me',
            'maxResults': min(max_results, 50)  # Limitar a máximo 50
        }
        
        if query:
            search_params['q'] = query
        if label_ids:
            search_params['labelIds'] = label_ids
        
        # Obtener lista de mensajes
        results = service.users().messages().list(**search_params).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "📬 No se encontraron mensajes que coincidan con los criterios de búsqueda."
        
        # Obtener detalles básicos de cada mensaje
        message_list = [f"📬 Mensajes encontrados ({len(messages)}):\n"]
        
        for msg in messages:
            try:
                msg_detail = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
                
                from_addr = headers.get('From', 'Desconocido')
                subject = headers.get('Subject', 'Sin asunto')
                date = headers.get('Date', 'Fecha desconocida')[:16]  # Solo fecha y hora
                
                message_list.append(f"📧 **{subject}**")
                message_list.append(f"   De: {from_addr}")
                message_list.append(f"   Fecha: {date}")
                message_list.append(f"   ID: {msg['id']}\n")
                
            except Exception as e:
                message_list.append(f"❌ Error al obtener detalles del mensaje {msg['id']}: {str(e)}\n")
        
        return "\n".join(message_list)
    except Exception as e:
        return f"❌ Error al listar mensajes: {str(e)}"


@tool
def get_message(message_id: str, format: str = 'full') -> str:
    """Recupera encabezados y cuerpo de un correo.
    
    Args:
        message_id: ID del mensaje a recuperar
        format: Formato del mensaje (full, metadata, minimal, raw)
        
    Returns:
        Detalles completos del mensaje incluyendo encabezados y contenido
    """
    try:
        service = get_gmail_service()
        
        # Obtener mensaje completo
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format=format
        ).execute()
        
        # Extraer encabezados
        headers = {}
        if 'payload' in message and 'headers' in message['payload']:
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        # Extraer contenido del cuerpo
        body_content = ""
        if 'payload' in message:
            body_content = extract_message_body(message['payload'])
        
        # Formatear respuesta
        result = [
            f"📧 **Detalles del mensaje:**\n",
            f"**ID:** {message.get('id', 'N/A')}",
            f"**Thread ID:** {message.get('threadId', 'N/A')}",
            f"**De:** {headers.get('From', 'Desconocido')}",
            f"**Para:** {headers.get('To', 'Desconocido')}",
            f"**Asunto:** {headers.get('Subject', 'Sin asunto')}",
            f"**Fecha:** {headers.get('Date', 'Fecha desconocida')}",
            f"**CC:** {headers.get('Cc', 'Ninguno')}",
            f"**BCC:** {headers.get('Bcc', 'Ninguno')}",
            f"\n**Contenido del mensaje:**\n{body_content[:1000]}{'...' if len(body_content) > 1000 else ''}"
        ]
        
        return "\n".join(result)
    except Exception as e:
        return f"❌ Error al recuperar el mensaje: {str(e)}"


@tool
def send_message(to: List[str], subject: str, body_html: str, cc: List[str] = None, bcc: List[str] = None) -> str:
    """Envía un email nuevo.
    
    Args:
        to: Lista de destinatarios principales
        subject: Asunto del mensaje
        body_html: Contenido HTML del mensaje
        cc: Lista de destinatarios en copia (opcional)
        bcc: Lista de destinatarios en copia oculta (opcional)
        
    Returns:
        Confirmación del envío del mensaje
    """
    try:
        service = get_gmail_service()
        
        # Crear mensaje MIME
        message = MIMEMultipart('alternative')
        message['To'] = ', '.join(to)
        message['Subject'] = subject
        
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        
        # Adjuntar contenido HTML
        html_part = MIMEText(body_html, 'html', 'utf-8')
        message.attach(html_part)
        
        # Codificar mensaje
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Enviar mensaje
        send_result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"✅ Mensaje enviado exitosamente a {', '.join(to)} (ID: {send_result['id']})"
    except Exception as e:
        return f"❌ Error al enviar el mensaje: {str(e)}"


@tool
def reply_message(thread_id: str, body_html: str, quote_original: bool = True) -> str:
    """Responde en el mismo hilo a un mensaje dado.
    
    Args:
        thread_id: ID del hilo al que responder
        body_html: Contenido HTML de la respuesta
        quote_original: Si incluir el mensaje original citado (opcional)
        
    Returns:
        Confirmación del envío de la respuesta
    """
    try:
        service = get_gmail_service()
        
        # Obtener el hilo original para extraer información
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        
        if not thread.get('messages'):
            return f"❌ No se encontraron mensajes en el hilo {thread_id}"
        
        # Obtener el último mensaje del hilo
        last_message = thread['messages'][-1]
        
        # Extraer encabezados del mensaje original
        headers = {}
        if 'payload' in last_message and 'headers' in last_message['payload']:
            headers = {h['name']: h['value'] for h in last_message['payload']['headers']}
        
        # Preparar respuesta
        original_subject = headers.get('Subject', '')
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        
        original_from = headers.get('From', '')
        reply_to = headers.get('Reply-To', original_from)
        
        # Crear mensaje de respuesta
        message = MIMEMultipart('alternative')
        message['To'] = reply_to
        message['Subject'] = reply_subject
        message['In-Reply-To'] = headers.get('Message-ID', '')
        message['References'] = headers.get('References', headers.get('Message-ID', ''))
        
        # Contenido de la respuesta
        final_body = body_html
        if quote_original:
            original_body = extract_message_body(last_message['payload'])
            quoted_body = '\n'.join(f"> {line}" for line in original_body.split('\n'))
            final_body += f"\n\n--- Mensaje original ---\n{quoted_body}"
        
        html_part = MIMEText(final_body, 'html', 'utf-8')
        message.attach(html_part)
        
        # Codificar y enviar
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_result = service.users().messages().send(
            userId='me',
            body={
                'raw': raw_message,
                'threadId': thread_id
            }
        ).execute()
        
        return f"✅ Respuesta enviada exitosamente en el hilo {thread_id} (ID: {send_result['id']})"
    except Exception as e:
        return f"❌ Error al enviar la respuesta: {str(e)}"


@tool
def delete_message(message_id: str, permanent: bool = False) -> str:
    """Borra definitivamente o mueve a papelera un mensaje.
    
    Args:
        message_id: ID del mensaje a eliminar
        permanent: Si es True, elimina permanentemente; si es False, mueve a papelera
        
    Returns:
        Confirmación de la eliminación del mensaje
    """
    try:
        service = get_gmail_service()
        
        if permanent:
            # Eliminación permanente
            service.users().messages().delete(userId='me', id=message_id).execute()
            action = "eliminado permanentemente"
        else:
            # Mover a papelera
            service.users().messages().trash(userId='me', id=message_id).execute()
            action = "movido a la papelera"
        
        return f"✅ Mensaje {action} exitosamente (ID: {message_id})"
    except Exception as e:
        return f"❌ Error al eliminar el mensaje: {str(e)}"


@tool
def modify_labels(message_id: str, add_label_ids: List[str] = None, remove_label_ids: List[str] = None) -> str:
    """Añade o quita labels (ej: marcar leído/no leído).
    
    Args:
        message_id: ID del mensaje a modificar
        add_label_ids: IDs de etiquetas a añadir (opcional)
        remove_label_ids: IDs de etiquetas a quitar (opcional)
        
    Returns:
        Confirmación de la modificación de etiquetas
    """
    try:
        service = get_gmail_service()
        
        if not add_label_ids and not remove_label_ids:
            return "❌ Debe especificar al menos una etiqueta para añadir o quitar"
        
        # Preparar modificaciones
        body = {}
        if add_label_ids:
            body['addLabelIds'] = add_label_ids
        if remove_label_ids:
            body['removeLabelIds'] = remove_label_ids
        
        # Aplicar modificaciones
        result = service.users().messages().modify(
            userId='me',
            id=message_id,
            body=body
        ).execute()
        
        # Preparar mensaje de confirmación
        actions = []
        if add_label_ids:
            actions.append(f"añadidas: {', '.join(add_label_ids)}")
        if remove_label_ids:
            actions.append(f"quitadas: {', '.join(remove_label_ids)}")
        
        return f"✅ Etiquetas {' y '.join(actions)} exitosamente en el mensaje {message_id}"
    except Exception as e:
        return f"❌ Error al modificar las etiquetas: {str(e)}"


# --- FUNCIONES AUXILIARES ---

def extract_message_body(payload):
    """Extrae el contenido del cuerpo del mensaje desde el payload."""
    body = ""
    
    if 'parts' in payload:
        # Mensaje con múltiples partes
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    # Para HTML, podrías querer procesarlo, por ahora lo devolvemos como está
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                # Recursivo para partes anidadas
                body += extract_message_body(part)
    else:
        # Mensaje simple
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return body
