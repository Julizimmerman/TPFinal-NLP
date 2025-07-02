"""Ejecutor especializado para tareas de clima."""
from langchain.agents import initialize_agent, AgentType
from datetime import datetime, timezone, timedelta
from ..config import LLM_EXECUTOR
from ..tools.weather import (
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice
)

# Fecha actual (BA)
BA = timezone(timedelta(hours=-3))
TODAY = datetime.now(BA).strftime("%-d de %B de %Y")

WEATHER_TOOLS = [
    get_weather,
    get_next_rain_day,
    geocode,
    get_air_quality,
    get_sun_times,
    get_weekly_summary,
    get_clothing_advice
]

WEATHER_EXECUTOR_PREFIX = f"""
Eres un agente especializado en información meteorológica con acceso a herramientas específicas.

*ATENCIÓN IMPORTANTE*: 
Ignora cualquier mención anterior al día de hoy en la conversación; la fecha de hoy es exactamente {TODAY}.

HERRAMIENTAS DISPONIBLES Y CÓMO USARLAS:

1. **get_weather(location)**: Obtiene el clima actual
   - Parámetro: location (string) - ciudad, país o coordenadas
   - Ejemplo: "Buenos Aires, Argentina" o "New York, USA"
   - Retorna: temperatura, condiciones, humedad, viento

2. **geocode(location)**: Convierte ubicación a coordenadas
   - Parámetro: location (string) - dirección o nombre de lugar
   - Ejemplo: "Plaza de Mayo, Buenos Aires"
   - Retorna: latitud, longitud, país, estado

3. **get_air_quality(location)**: Obtiene calidad del aire
   - Parámetro: location (string) - ciudad o coordenadas
   - Retorna: índice AQI, contaminantes, recomendaciones

4. **get_sun_times(location)**: Horarios de sol
   - Parámetro: location (string) - ciudad o coordenadas
   - Retorna: salida, puesta, duración del día

5. **get_clothing_advice(location)**: Consejos de vestimenta
   - Parámetro: location (string) - ciudad o coordenadas
   - Retorna: recomendaciones basadas en temperatura y condiciones

6. **get_weekly_summary(location)**: Pronóstico semanal
   - Parámetro: location (string) - ciudad o coordenadas
   - Retorna: resumen de 7 días con temperaturas y condiciones

7. **get_next_rain_day(location)**: Próximo día de lluvia
   - Parámetro: location (string) - ciudad o coordenadas
   - Retorna: fecha y probabilidad de lluvia

INSTRUCCIONES DE EJECUCIÓN:
- SIEMPRE especifica qué herramienta vas a usar antes de usarla
- Si una herramienta falla, explica exactamente por qué
- Proporciona respuestas estructuradas y claras
- Incluye unidades de medida (Celsius, km/h, etc.)
- Si no puedes obtener información, explica el motivo específico

FORMATO DE RESPUESTA:
1. "Voy a usar [HERRAMIENTA] para [PROPÓSITO]"
2. "Resultado: [DESCRIPCIÓN CLARA DEL RESULTADO]"
3. "Estado: [EXITOSO/FRACASO] - [EXPLICACIÓN]"
"""

weather_executor = initialize_agent(
    WEATHER_TOOLS,
    LLM_EXECUTOR,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    agent_kwargs={"system_message": WEATHER_EXECUTOR_PREFIX},
    max_iterations=5,
    max_execution_time=30,
    early_stopping_method="generate",
    handle_parsing_errors=True,
)

async def execute_weather_task(task: str) -> str:
    print(f"🌤️ [WEATHER_EXECUTOR] Ejecutando tarea: {task}")
    try:
        response = await weather_executor.ainvoke({"input": task})
        result = response["output"]
        print(f"🌤️ [WEATHER_EXECUTOR] Resultado: {result}")
        return result
    except Exception as e:
        error_msg = f"Error en weather_executor: {str(e)}"
        print(f"🌤️ [WEATHER_EXECUTOR] {error_msg}")
        return error_msg 