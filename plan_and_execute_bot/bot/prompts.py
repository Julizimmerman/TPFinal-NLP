from langchain.prompts import PromptTemplate
from datetime import datetime, timezone, timedelta
BA = timezone(timedelta(hours=-3))      # tu huso horario
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")



BASE_PROMPT = """Eres el módulo de planificación de un asistente de IA con memoria de conversación.

*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.

    
Contexto y solicitud del usuario: {input}

Analiza la entrada cuidadosamente. Si contiene historial de conversación, considera el contexto previo al planificar.
Si el usuario se refiere a información anterior (como "esa ciudad", "el clima que pregunté", etc.), 
usa el contexto de la conversación para entender a qué se refiere.

Divide la solicitud en una lista concisa y ordenada de pasos.
Responde SOLO con pasos numerados.

Ejemplos:
- Si el usuario pregunta "¿Cuál es el clima en Madrid?" → "1. Obtener el clima actual de Madrid"
- Si el usuario luego pregunta "¿Y mañana?" → "1. Obtener el pronóstico del clima para Madrid para mañana"
- Si el usuario pregunta "¿Qué tal Barcelona?" → "1. Obtener el clima actual de Barcelona"
- Si el usuario dice "Enviale un mail a Maria Lopez para confirmar la reunion" - 1. Construir la direccion de correo de Maria lopez: "mlopez@udesa.edu.ar" 
                                                                                 2. Usar Gmail.send_message con destinatario "mlopez@udesa.edu.ar" y contenido apropiado
                                                                                 3. Responder al usuario confirmando que el mail se envió
- Si el usuario dice "Enviale un mail a marialopez@gmail.com" - 1. Usar Gmail.send_message con destinatario "marialopez@gmail.com" y contenido apropiado
                                                                2. Responder al usuario confirmando que el mail se envió
"""


PLANNER_PROMPT = (
    PromptTemplate
    .from_template(BASE_PROMPT)
    .partial(TODAY=TODAY)
)

REPLANNER_PROMPT = PromptTemplate.from_template(
    """Estás actualizando un plan de múltiples pasos con conciencia de conversación.


Solicitud del usuario: {input}

Plan original:
{plan}

Pasos ya completados:
{past_steps}

Considera el contexto de la conversación al decidir los próximos pasos. Si el usuario está haciendo preguntas de seguimiento
o refiriéndose a información anterior, asegúrate de que el plan aborde su intención real.

Devuelve CUALQUIERA DE LAS DOS OPCIONES:
1) "RESPUESTA: <respuesta final>" si la tarea está completa, O
2) "PLAN: <nuevo plan numerado>" si quedan más pasos.
NO repitas pasos completados.

Ejemplo:
- Plan original:
  1. Usar Calendar.create_event para crear "Reunión con Carlos García" mañana a las 10 AM.
  2. Enviar email de confirmación a Carlos García.
- Usuario dice: "Finalmente, que la reunión sea con Ana Fernández."  
  → Salida:
  PLAN:
  1. **Construir email de Ana Fernández: "afernandez@udesa.edu.ar".**  
  2. Usar Calendar.search_event para buscar evento "Reunión con Carlos García" mañana.  
  3. Usar Calendar.update_event con el ID obtenido para cambiar título a "Reunión con Ana Fernández".  
  4. Usar Gmail.send_message para notificar a "afernandez@udesa.edu.ar" que la reunión fue reasignada.  
  5. Responder al usuario confirmando la reasignación.  

Ejemplo:
- Plan original:
  1. Usar Calendar.create_event para crear "Reunión con Carlos García" mañana a las 10 AM.
  2. Enviar email de confirmación a Carlos García.
- Usuario dice: "Finalmente, que la reunión sea con juanita@gmail.com."  
  → Salida:
  PLAN:
  2. Usar Calendar.search_event para buscar evento "Reunión con Carlos García" mañana.  
  3. Usar Calendar.update_event con el ID obtenido para cambiar título a "Reunión con Juanita".  
  4. Usar Gmail.send_message para notificar a "juanita@gmail.com" que la reunión fue reasignada.  
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
