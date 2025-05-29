# drive_folder.py

import io
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# --- CONFIGURACIÓN OAuth ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'drive_token.json'


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

# --- FUNCIONES DE CARPETA ---

def get_folder_id(name: str) -> str:
    """Devuelve el ID de la carpeta dado su nombre, o None si no existe."""
    service = get_drive_service()
    resp = service.files().list(
        q=f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'",
        spaces='drive',
        fields='files(id)',
        pageSize=1
    ).execute()
    items = resp.get('files', [])
    return items[0]['id'] if items else None


def create_folder(name: str) -> str:
    """Crea una carpeta en Drive y devuelve su ID."""
    service = get_drive_service()
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']


def ensure_folder(name: str) -> str:
    """Devuelve el ID de la carpeta, creándola si no existe."""
    folder_id = get_folder_id(name)
    if not folder_id:
        folder_id = create_folder(name)
    return folder_id

# --- FUNCIONES DE ARCHIVOS ---

def create_file(name: str,
                folder_name: str,
                mime_type: str = 'application/vnd.google-apps.document') -> str:
    """
    Crea un archivo vacío en Google Drive con el MIME type especificado.
    """
    service = get_drive_service()
    folder_id = ensure_folder(folder_name)
    metadata = {'name': name, 'mimeType': mime_type, 'parents': [folder_id]}
    file = service.files().create(body=metadata, fields='id,name,mimeType').execute()
    return f"Creado: «{file['name']}» (id: {file['id']}, tipo: {file['mimeType']})"


def write_file(local_path: str,
               folder_name: str,
               convert_to_mime: str = None) -> str:
    """
    Sube o reemplaza un archivo local a Drive dentro de la carpeta.
    Si `convert_to_mime` se especifica, convierte el archivo local al formato nativo de Google.
    """
    service = get_drive_service()
    folder_id = ensure_folder(folder_name)
    file_name = Path(local_path).name
    metadata = {'name': file_name, 'parents': [folder_id]}
    if convert_to_mime:
        metadata['mimeType'] = convert_to_mime
    media = MediaFileUpload(local_path, resumable=True)
    existing_id = get_file_id(file_name, folder_name)
    if existing_id:
        updated = service.files().update(
            fileId=existing_id,
            body=metadata,
            media_body=media,
            fields='id,name,mimeType'
        ).execute()
        return f"Reemplazado: «{updated['name']}» (id: {updated['id']}, tipo: {updated['mimeType']})"
    else:
        created = service.files().create(
            body=metadata,
            media_body=media,
            fields='id,name,mimeType'
        ).execute()
        return f"Subido: «{created['name']}» (id: {created['id']}, tipo: {created['mimeType']})"


def read_file(name: str,
              folder_name: str,
              export_mime: str = 'text/plain') -> bytes:
    """
    Descarga el contenido de un archivo de Drive.
    - Para archivos nativos de Google, lo exporta en el formato `export_mime`.
    - Para archivos binarios comunes, lo descarga tal cual.
    """
    service = get_drive_service()
    file_id = get_file_id(name, folder_name)
    if not file_id:
        raise FileNotFoundError(f"No se encontró «{name}» en «{folder_name}».")
    meta = service.files().get(fileId=file_id, fields='mimeType').execute()
    mime = meta.get('mimeType')
    if mime.startswith('application/vnd.google-apps'):
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer.read()


def get_file_id(name: str, folder_name: str) -> str:
    """Devuelve el ID de un archivo por nombre dentro de la carpeta (primer match)."""
    service = get_drive_service()
    folder_id = ensure_folder(folder_name)
    q = f"name = '{name}' and '{folder_id}' in parents"
    resp = service.files().list(q=q, spaces='drive', fields='files(id)', pageSize=1).execute()
    items = resp.get('files', [])
    return items[0]['id'] if items else None

# --- EJEMPLOS DE USO ---
if __name__ == '__main__':
    # Crear un Google Doc vacío
    print(create_file('Documento de prueba', 'MiCarpetaNLP', 'application/vnd.google-apps.document'))

    # Subir y convertir archivos locales:
    print(write_file('informe.docx', 'MiCarpetaNLP', convert_to_mime='application/vnd.google-apps.document'))
    print(write_file('datos.xlsx', 'MiCarpetaNLP', convert_to_mime='application/vnd.google-apps.spreadsheet'))
    print(write_file('test.pdf', 'MiCarpetaNLP'))  # sube PDF tal cual

    # Leer/descargar archivos:
    texto = read_file('Documento de prueba', 'MiCarpetaNLP', export_mime='text/plain')
    print(texto.decode()[:200])

    # Descargar el PDF previamente subido (test.pdf)
    pdf_bytes = read_file('test.pdf', 'MiCarpetaNLP')
    with open('salida_test.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print('PDF descargado como salida_test.pdf')
