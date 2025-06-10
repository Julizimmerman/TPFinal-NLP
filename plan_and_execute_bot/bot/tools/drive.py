# drive.py

import io
import base64
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from langchain.tools import tool

# --- CONFIGURACIÓN OAuth ---
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents'
]

# Configurar rutas relativas al directorio del bot
_CURRENT_DIR = Path(__file__).parent.parent.parent  # Subir 3 niveles desde bot/tools/drive.py
CREDS_FILE = 'credentials.json'
TOKEN_FILE = str(_CURRENT_DIR / 'drive_token.json')


def get_drive_service():
    """Inicializa y devuelve el servicio de Google Drive."""
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
    return build('drive', 'v3', credentials=creds)


@tool
def search_files(query: str, page_size: int = 10) -> str:
    """Busca archivos/carpetas por nombre, tipo o propietario.
    
    Args:
        query: Término de búsqueda (nombre, tipo de archivo, etc.)
        page_size: Número máximo de resultados a devolver (opcional, por defecto 10)
        
    Returns:
        Lista de archivos que coinciden con la búsqueda
    """
    try:
        service = get_drive_service()
        
        # Construir query de búsqueda
        search_query = f"name contains '{query}' or fullText contains '{query}'"
        
        results = service.files().list(
            q=search_query,
            spaces='drive',
            fields='files(id,name,mimeType,parents,modifiedTime,size)',
            pageSize=min(page_size, 50)  # Limitar a máximo 50
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            return f"🔍 No se encontraron archivos que coincidan con '{query}'"
        
        file_list = [f"🔍 Resultados de búsqueda para '{query}' ({len(files)} encontrados):\n"]
        for file in files:
            file_type = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
            modified = file.get('modifiedTime', 'N/A')[:10]
            size = file.get('size', 'N/A')
            file_list.append(f"{file_type} **{file['name']}** (ID: {file['id']}) - Tamaño: {size}, Modificado: {modified}")
        
        return "\n".join(file_list)
    except Exception as e:
        return f"❌ Error al buscar archivos: {str(e)}"


@tool
def get_file_metadata(file_id: str) -> str:
    """Devuelve metadatos de un archivo (tamaño, mime-type, etc.).
    
    Args:
        file_id: ID del archivo en Google Drive
        
    Returns:
        Metadatos detallados del archivo
    """
    try:
        service = get_drive_service()
        
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,size,createdTime,modifiedTime,parents,owners,shared'
        ).execute()
        
        metadata_info = [
            f"📄 **Metadatos del archivo:**\n",
            f"• **Nombre:** {file_metadata.get('name', 'N/A')}",
            f"• **ID:** {file_metadata.get('id', 'N/A')}",
            f"• **Tipo MIME:** {file_metadata.get('mimeType', 'N/A')}",
            f"• **Tamaño:** {file_metadata.get('size', 'N/A')} bytes",
            f"• **Creado:** {file_metadata.get('createdTime', 'N/A')[:19]}",
            f"• **Modificado:** {file_metadata.get('modifiedTime', 'N/A')[:19]}",
            f"• **Compartido:** {'Sí' if file_metadata.get('shared', False) else 'No'}"
        ]
        
        return "\n".join(metadata_info)
    except Exception as e:
        return f"❌ Error al obtener metadatos del archivo: {str(e)}"


@tool
def download_file(file_id: str, export_mime_type: str = None) -> str:
    """Descarga el contenido de un archivo.
    
    Args:
        file_id: ID del archivo en Google Drive
        export_mime_type: Tipo MIME para exportar archivos de Google (opcional)
        
    Returns:
        Confirmación de descarga con información del archivo
    """
    try:
        service = get_drive_service()
        
        # Obtener metadatos del archivo
        file_metadata = service.files().get(fileId=file_id, fields='name,mimeType').execute()
        file_name = file_metadata.get('name')
        mime_type = file_metadata.get('mimeType')
        
        # Determinar si necesita exportación
        if mime_type.startswith('application/vnd.google-apps'):
            # Archivo nativo de Google - necesita exportación
            if not export_mime_type:
                export_mime_type = 'text/plain'  # Por defecto
            request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            file_extension = export_mime_type.split('/')[-1]
            local_filename = f"{file_name}.{file_extension}"
        else:
            # Archivo regular
            request = service.files().get_media(fileId=file_id)
            local_filename = file_name
        
        # Descargar el archivo
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        # Guardar archivo localmente
        buffer.seek(0)
        with open(local_filename, 'wb') as f:
            f.write(buffer.read())
        
        return f"✅ Archivo '{file_name}' descargado exitosamente como '{local_filename}'"
    except Exception as e:
        return f"❌ Error al descargar el archivo: {str(e)}"


@tool
def upload_file(name: str, mime_type: str, data: str, parent_folder_id: str = None) -> str:
    """Sube un archivo nuevo o nueva versión.
    
    Args:
        name: Nombre del archivo
        mime_type: Tipo MIME del archivo
        data: Contenido del archivo en base64
        parent_folder_id: ID de la carpeta padre (opcional)
        
    Returns:
        Confirmación de la subida del archivo
    """
    try:
        service = get_drive_service()
        
        # Decodificar datos base64
        file_content = base64.b64decode(data)
        
        # Preparar metadatos
        metadata = {'name': name, 'mimeType': mime_type}
        if parent_folder_id:
            metadata['parents'] = [parent_folder_id]
        
        # Crear media upload desde bytes
        media = MediaIoBaseUpload(
            io.BytesIO(file_content),
            mimetype=mime_type,
            resumable=True
        )
        
        # Subir archivo
        file_result = service.files().create(
            body=metadata,
            media_body=media,
            fields='id,name,mimeType'
        ).execute()
        
        return f"✅ Archivo '{file_result['name']}' subido exitosamente (ID: {file_result['id']})"
    except Exception as e:
        return f"❌ Error al subir el archivo: {str(e)}"


@tool
def move_file(file_id: str, new_parent_id: str) -> str:
    """Cambia de carpeta o reubica un archivo.
    
    Args:
        file_id: ID del archivo a mover
        new_parent_id: ID de la nueva carpeta padre
        
    Returns:
        Confirmación del movimiento del archivo
    """
    try:
        service = get_drive_service()
        
        # Obtener los padres actuales
        file_metadata = service.files().get(fileId=file_id, fields='parents,name').execute()
        current_parents = file_metadata.get('parents', [])
        file_name = file_metadata.get('name')
        
        # Mover el archivo
        service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=','.join(current_parents),
            fields='id,parents'
        ).execute()
        
        return f"✅ Archivo '{file_name}' movido exitosamente a la nueva ubicación (ID: {file_id})"
    except Exception as e:
        return f"❌ Error al mover el archivo: {str(e)}"


@tool
def delete_file(file_id: str, permanent: bool = False) -> str:
    """Envía un archivo a la papelera o lo elimina permanentemente.
    
    Args:
        file_id: ID del archivo a eliminar
        permanent: Si es True, elimina permanentemente; si es False, envía a papelera
        
    Returns:
        Confirmación de la eliminación del archivo
    """
    try:
        service = get_drive_service()
        
        # Obtener nombre del archivo antes de eliminarlo
        file_metadata = service.files().get(fileId=file_id, fields='name').execute()
        file_name = file_metadata.get('name')
        
        if permanent:
            # Eliminación permanente
            service.files().delete(fileId=file_id).execute()
            action = "eliminado permanentemente"
        else:
            # Enviar a papelera
            service.files().update(fileId=file_id, body={'trashed': True}).execute()
            action = "enviado a la papelera"
        
        return f"✅ Archivo '{file_name}' {action} exitosamente"
    except Exception as e:
        return f"❌ Error al eliminar el archivo: {str(e)}"



