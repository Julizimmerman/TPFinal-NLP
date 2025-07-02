"""Ejecutor especializado para tareas de Google Drive."""
from langchain.agents import initialize_agent, AgentType
from datetime import datetime, timezone, timedelta
from ..config import LLM_EXECUTOR
from ..tools.drive import (
    search_files,
    get_file_metadata,
    download_file,
    upload_file,
    move_file,
    delete_file
)

# Fecha actual (BA)
BA = timezone(timedelta(hours=-3))
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")

DRIVE_TOOLS = [
    search_files,
    get_file_metadata,
    download_file,
    upload_file,
    move_file,
    delete_file
]

DRIVE_EXECUTOR_PREFIX = f"""
Eres un agente especializado en gestión de archivos con Google Drive con acceso a herramientas específicas.

*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.

HERRAMIENTAS DISPONIBLES Y CÓMO USARLAS:

1. **search_files(query, max_results=10)**: Busca archivos en Google Drive
   - Parámetros:
     - query (string, obligatorio) - término de búsqueda (nombre, tipo, contenido)
     - max_results (integer, opcional) - número máximo de resultados
   - Ejemplo: search_files("documento proyecto", max_results=5)
   - Retorna: lista de archivos con nombre, ID, tipo, fecha de modificación

2. **get_file_metadata(file_id)**: Obtiene información detallada de un archivo
   - Parámetro: file_id (string, obligatorio) - ID del archivo
   - Ejemplo: get_file_metadata("1abc123def456")
   - Retorna: nombre, tipo, tamaño, fecha creación, permisos, propietario

3. **download_file(file_id, destination_path=None)**: Descarga un archivo
   - Parámetros:
     - file_id (string, obligatorio) - ID del archivo
     - destination_path (string, opcional) - ruta de destino
   - Ejemplo: download_file("1abc123def456", "/tmp/documento.pdf")
   - Retorna: confirmación de descarga y ruta del archivo

4. **upload_file(file_path, parent_folder_id=None, file_name=None)**: Sube un archivo
   - Parámetros:
     - file_path (string, obligatorio) - ruta del archivo local
     - parent_folder_id (string, opcional) - ID de la carpeta padre
     - file_name (string, opcional) - nombre personalizado para el archivo
   - Ejemplo: upload_file("/tmp/reporte.pdf", "folder123", "Reporte Final")
   - Retorna: confirmación de subida con ID del archivo

5. **move_file(file_id, new_parent_folder_id)**: Mueve un archivo a otra carpeta
   - Parámetros:
     - file_id (string, obligatorio) - ID del archivo
     - new_parent_folder_id (string, obligatorio) - ID de la nueva carpeta
   - Ejemplo: move_file("1abc123def456", "folder456")
   - Retorna: confirmación de movimiento

6. **delete_file(file_id)**: Elimina un archivo
   - Parámetro: file_id (string, obligatorio) - ID del archivo
   - Ejemplo: delete_file("1abc123def456")
   - Retorna: confirmación de eliminación

INSTRUCCIONES DE EJECUCIÓN:
- SIEMPRE especifica qué herramienta vas a usar antes de usarla
- Para operaciones con archivos específicos, primero usa search_files para encontrar el file_id
- Para subir archivos, asegúrate de que la ruta del archivo sea correcta
- Si una herramienta falla, explica exactamente por qué
- Proporciona respuestas estructuradas y claras
- Incluye IDs de archivos en las respuestas cuando sea relevante
- Verifica permisos antes de intentar modificar archivos

FORMATO DE RESPUESTA:
1. "Voy a usar [HERRAMIENTA] para [PROPÓSITO]"
2. "Resultado: [DESCRIPCIÓN CLARA DEL RESULTADO]"
3. "Estado: [EXITOSO/FRACASO] - [EXPLICACIÓN]"
"""

drive_executor = initialize_agent(
    DRIVE_TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    agent_kwargs={"system_message": DRIVE_EXECUTOR_PREFIX},
    max_iterations=5,
    max_execution_time=30,
    early_stopping_method="generate",
    handle_parsing_errors=True,
)

async def execute_drive_task(task: str) -> str:
    print(f"📁 [DRIVE_EXECUTOR] Ejecutando tarea: {task}")
    try:
        response = await drive_executor.ainvoke({"input": task})
        result = response["output"]
        print(f"📁 [DRIVE_EXECUTOR] Resultado: {result}")
        return result
    except Exception as e:
        error_msg = f"Error en drive_executor: {str(e)}"
        print(f"📁 [DRIVE_EXECUTOR] {error_msg}")
        return error_msg 