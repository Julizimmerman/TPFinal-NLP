from langchain.prompts import PromptTemplate
from datetime import datetime, timezone, timedelta
BA = timezone(timedelta(hours=-3))      # tu huso horario
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")

# Lista de herramientas disponibles para incluir en el prompt
AVAILABLE_TOOLS = """

🔧 HERRAMIENTAS DISPONIBLES:

📅 CLIMA:
- get_weather(location): Clima actual (temperatura, descripción, humedad)
- get_weekly_summary(location): Resumen de temperaturas min/max próximos 5 días
- get_next_rain_day(location): Primer día con lluvia en próximos 5 días
- get_sun_times(location): Horarios de salida y puesta del sol
- get_air_quality(location): Índice de calidad del aire (AQI)
- get_clothing_advice(location): Recomendación de vestimenta según clima
- geocode(location): Obtener coordenadas (lat, lon) de ubicación

📋 TAREAS (Google Tasks):
- create_task(title): Crear nueva tarea
- list_tasks(): Listar todas las tareas pendientes  
- complete_task(task_title): Marcar tarea como completada
- delete_task(task_title): Eliminar tarea
- edit_task(task_title, new_title=None, new_notes=None): Editar tarea existente
- search_tasks(keyword): Buscar tareas por palabra clave

📁 GOOGLE DRIVE:
- search_files(query, page_size=10): Buscar archivos/carpetas
- get_file_metadata(file_id): Obtener metadatos de archivo
- download_file(file_id, export_mime_type=None): Descargar archivo
- upload_file(name, mime_type, data, parent_folder_id=None): Subir archivo
- move_file(file_id, new_parent_id): Mover archivo a otra carpeta
- delete_file(file_id, permanent=False): Eliminar archivo (papelera o permanente)

📧 GMAIL:
- list_messages(query=None, label_ids=None, max_results=10): Listar mensajes
- get_message(message_id): Obtener mensaje específico
- send_message(to, subject, body_html, cc=None, bcc=None): Enviar email
- reply_message(message_id, body_html): Responder a mensaje
- delete_message(message_id, permanent=False): Eliminar mensaje
- modify_labels(message_id, add_labels=None, remove_labels=None): Modificar etiquetas

📅 GOOGLE CALENDAR:
- list_calendars(): Listar calendarios disponibles
- list_events(calendar_id, time_min, time_max, query=None): Listar eventos
- get_event(calendar_id, event_id): Obtener evento específico
- create_event(calendar_id, summary, start_time, end_time, description=None): Crear evento
- update_event(calendar_id, event_id, summary=None, start_time=None, end_time=None): Actualizar evento
- delete_event(calendar_id, event_id): Eliminar evento
- find_free_slot(participants, duration_minutes, time_min=None, time_max=None): Encontrar horarios libres

"""

BASE_PROMPT = f"""Eres el módulo de planificación de un asistente de IA con memoria de conversación.

*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {{TODAY}}.

{AVAILABLE_TOOLS}
    
Contexto y solicitud del usuario: {{input}}

Analiza la entrada cuidadosamente. Si contiene historial de conversación, considera el contexto previo al planificar.
Si el usuario se refiere a información anterior (como "esa ciudad", "el clima que pregunté", etc.), 
usa el contexto de la conversación para entender a qué se refiere.

Divide la solicitud en una lista concisa y ordenada de pasos, USANDO ÚNICAMENTE LAS HERRAMIENTAS LISTADAS ARRIBA.
Responde SOLO con pasos numerados.

Ejemplos:
- Si el usuario pregunta "¿Cuál es el clima en Madrid?" → "1. Usar get_weather('Madrid')"
- Si el usuario luego pregunta "¿Y mañana?" → "1. Usar get_weekly_summary('Madrid')"
- Si el usuario pregunta "¿Qué tal Barcelona?" → "1. Usar get_weather('Barcelona')"
- Si el usuario dice "Enviale un mail a Maria Lopez para confirmar la reunion" → "1. Construir la direccion de correo de Maria Lopez: 'mlopez@udesa.edu.ar'
                                                                                 2. Usar send_message(['mlopez@udesa.edu.ar'], 'Confirmación de reunión', contenido apropiado)
                                                                                 3. Responder al usuario confirmando que el mail se envió"
- Si el usuario dice "Enviale un mail a marialopez@gmail.com" → "1. Usar send_message(['marialopez@gmail.com'], asunto apropiado, contenido apropiado)
                                                                2. Responder al usuario confirmando que el mail se envió"
"""


PLANNER_PROMPT = (
    PromptTemplate
    .from_template(BASE_PROMPT)
    .partial(TODAY=TODAY)
)

REPLANNER_PROMPT = PromptTemplate.from_template(
    f"""Estás actualizando un plan de múltiples pasos con conciencia de conversación.

{AVAILABLE_TOOLS}

Solicitud del usuario: {{input}}

Plan original:
{{plan}}

Pasos ya completados:
{{past_steps}}

Considera el contexto de la conversación al decidir los próximos pasos. Si el usuario está haciendo preguntas de seguimiento
o refiriéndose a información anterior, asegúrate de que el plan aborde su intención real.

IMPORTANTE: Usa únicamente las herramientas listadas arriba al crear el nuevo plan.

Devuelve CUALQUIERA DE LAS DOS OPCIONES:
1) "RESPUESTA: <respuesta final>" si la tarea está completa, O
2) "PLAN: <nuevo plan numerado>" si quedan más pasos.
NO repitas pasos completados.

Ejemplo:
- Plan original:
  1. Usar create_event para crear "Reunión con Carlos García" mañana a las 10 AM.
  2. Enviar email de confirmación a Carlos García.
- Usuario dice: "Finalmente, que la reunión sea con Ana Fernández."  
  → Salida:
  PLAN:
  1. **Construir email de Ana Fernández: "afernandez@udesa.edu.ar".**  
  2. Usar list_events para buscar evento "Reunión con Carlos García" mañana.  
  3. Usar update_event con el ID obtenido para cambiar título a "Reunión con Ana Fernández".  
  4. Usar send_message para notificar a "afernandez@udesa.edu.ar" que la reunión fue reasignada.  
  5. Responder al usuario confirmando la reasignación.  

Ejemplo:
- Plan original:
  1. Usar create_event para crear "Reunión con Carlos García" mañana a las 10 AM.
  2. Enviar email de confirmación a Carlos García.
- Usuario dice: "Finalmente, que la reunión sea con juanita@gmail.com."  
  → Salida:
  PLAN:
  2. Usar list_events para buscar evento "Reunión con Carlos García" mañana.  
  3. Usar update_event con el ID obtenido para cambiar título a "Reunión con Juanita".  
  4. Usar send_message para notificar a "juanita@gmail.com" que la reunión fue reasignada.  
  5. Responder al usuario confirmando la reasignación. 
"""
)

EXECUTOR_PREFIX = f"""Eres el agente de ejecución con conciencia de conversación.

*ATENCIÓN IMPORTANTE*: 
    Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.

INSTRUCCIONES IMPORTANTES:
- Lleva a cabo la subtarea asignada y responde de manera concisa.
- Si la tarea se refiere al contexto de conversación anterior, usa esa información apropiadamente.
- Si te piden ejecutar múltiples pasos relacionados, usa múltiples herramientas en secuencia.
- Para tareas como "crear varias tareas", "listar y luego completar", etc., usa las herramientas necesarias en orden.
- No te limites a una sola herramienta si la tarea requiere varios pasos.
- Ejecuta todas las acciones solicitadas antes de responder.

EJEMPLOS DE USO MÚLTIPLE:
- "Crear tarea X y tarea Y" → usa create_task dos veces
- "Listar tareas y completar X" → usa list_tasks luego complete_task
- "Buscar tareas con palabra X y eliminar la primera" → usa search_tasks luego delete_task
- "Obtener clima y consejo de ropa" → usa get_weather luego get_clothing_advice

- Si en el paso aparece el nombre y apellido de alguna persona en contexto de correo o calendario, **construye su dirección de e-mail** como: [primera letra del nombre + apellido completo + "@udesa.edu.ar"]
Ejemplo: "Alejandro Ramos" → "aramos@udesa.edu.ar".

- Si en el paso aparece la direccion de correo electrónico en lugar de nombres y apellidos, mantene la direccion de e-mail que propuso el usuario. 
Ejemplo: "juanita@gmail.com"  → "juanita@gmail.com"

"""
