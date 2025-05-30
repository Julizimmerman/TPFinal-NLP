# Configuración de Herramientas de Google Drive

Este documento explica cómo configurar y usar las herramientas de Google Drive integradas en el chatbot.

## 📋 Herramientas Disponibles

El chatbot ahora incluye **7 herramientas de Google Drive**:

### 1. `drive_create_folder`
- **Función**: Crear carpetas en Google Drive
- **Parámetros**: `folder_name` (nombre de la carpeta)
- **Ejemplo**: "Crea una carpeta llamada 'Proyecto NLP'"

### 2. `drive_create_document`
- **Función**: Crear documentos de Google Docs vacíos
- **Parámetros**: `document_name`, `folder_name`
- **Ejemplo**: "Crea un documento llamado 'Informe' en la carpeta 'Proyecto NLP'"

### 3. `drive_create_spreadsheet`
- **Función**: Crear hojas de cálculo de Google Sheets vacías
- **Parámetros**: `spreadsheet_name`, `folder_name`
- **Ejemplo**: "Crea una hoja de cálculo llamada 'Datos' en la carpeta 'Proyecto NLP'"

### 4. `drive_upload_file`
- **Función**: Subir archivos locales a Google Drive
- **Parámetros**: `local_file_path`, `folder_name`
- **Ejemplo**: "Sube el archivo './informe.pdf' a la carpeta 'Documentos'"

### 5. `drive_download_file`
- **Función**: Descargar archivos de Google Drive al sistema local
- **Parámetros**: `file_name`, `folder_name`, `local_save_path` (opcional)
- **Ejemplo**: "Descarga el archivo 'informe.pdf' de la carpeta 'Documentos'"

### 6. `drive_list_files`
- **Función**: Listar archivos en una carpeta específica
- **Parámetros**: `folder_name`
- **Ejemplo**: "Lista todos los archivos en la carpeta 'Proyecto NLP'"

### 7. `drive_search_files`
- **Función**: Buscar archivos por nombre o contenido
- **Parámetros**: `search_query`
- **Ejemplo**: "Busca archivos que contengan 'machine learning'"

## 🔧 Configuración Inicial

### Paso 1: Credenciales de Google API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Drive API**
4. Crea credenciales OAuth 2.0:
   - Ve a "Credenciales" → "Crear credenciales" → "ID de cliente OAuth"
   - Tipo de aplicación: "Aplicación de escritorio"
   - Descarga el archivo JSON

### Paso 2: Configurar Credenciales

1. Renombra el archivo descargado a `credentials.json`
2. Colócalo en el directorio raíz del proyecto:
   ```
   TPFinal-NLP/
   ├── credentials.json  ← Aquí
   └── plan_and_execute_bot/
   ```

### Paso 3: Configurar Scopes (Opcional)

Las herramientas usan por defecto el scope `https://www.googleapis.com/auth/drive.file`, que permite:
- Crear archivos y carpetas
- Modificar archivos creados por la aplicación
- Leer archivos abiertos por el usuario

Para acceso completo a Drive, puedes cambiar en `drive.py`:
```python
SCOPES = ['https://www.googleapis.com/auth/drive']
```

## 🚀 Primer Uso

### Autenticación OAuth

La primera vez que uses una herramienta de Drive:

1. Se abrirá un navegador web automáticamente
2. Autoriza la aplicación con tu cuenta de Google
3. Se creará automáticamente `drive_token.json` para futuros usos

### Ejemplo de Uso en el Chatbot

```
Usuario: "Crea una carpeta llamada 'Trabajo NLP' y dentro crea un documento llamado 'Plan de proyecto'"

Chatbot: 
✅ Carpeta 'Trabajo NLP' creada exitosamente en Google Drive (ID: 1x2y3z...)
✅ Documento 'Plan de proyecto' creado exitosamente en la carpeta 'Trabajo NLP' (ID: 4a5b6c...)
```

## 🔍 Verificación de Instalación

Ejecuta el script de prueba para verificar que todo esté configurado:

```bash
python test_drive_tools.py
```

**Salida esperada**:
```
🎉 ¡Todas las pruebas pasaron! Las herramientas de Google Drive están listas para usar.
```

## 📁 Estructura de Archivos

```
TPFinal-NLP/
├── credentials.json          # Credenciales OAuth (no incluir en git)
├── drive_token.json         # Token generado automáticamente
├── test_drive_tools.py      # Script de prueba
└── plan_and_execute_bot/
    └── bot/
        └── tools/
            └── drive.py     # Herramientas de Google Drive
```

## ⚠️ Consideraciones de Seguridad

1. **Nunca subas `credentials.json` a git**
2. Añade estos archivos a `.gitignore`:
   ```
   credentials.json
   drive_token.json
   ```

3. Las herramientas manejan errores automáticamente y devuelven mensajes informativos

## 🔄 Flujos de Trabajo Comunes

### Crear Estructura de Proyecto
```
Usuario: "Crea una estructura para mi proyecto: 
- Carpeta 'Proyecto Machine Learning'
- Dentro, un documento 'Propuesta' 
- Y una hoja de cálculo 'Dataset'"
```

### Gestionar Archivos Locales
```
Usuario: "Sube mi archivo 'modelo.py' a la carpeta 'Código' y lista todo lo que hay ahí"
```

### Organizar Documentos
```
Usuario: "Busca todos los archivos que contengan 'tensorflow' y muéstrame qué encontraste"
```

## 🐛 Solución de Problemas

### Error: "No module named 'google'"
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### Error: "credentials.json not found"
- Verifica que `credentials.json` esté en el directorio raíz
- Verifica que el formato del archivo sea correcto

### Error de Autenticación
- Elimina `drive_token.json` y vuelve a autenticarte
- Verifica que las credenciales OAuth no hayan expirado

## 📊 Estado Actual

✅ **Completado**:
- 7 herramientas de Google Drive implementadas
- Integración con el sistema de chatbot
- Manejo de errores robusto
- Documentación completa

🔄 **Posibles Mejoras Futuras**:
- Herramientas para Google Docs API (editar contenido directamente)
- Integración con Google Sheets API (manipular datos)
- Compartir archivos y gestionar permisos
- Sincronización bidireccional de archivos 