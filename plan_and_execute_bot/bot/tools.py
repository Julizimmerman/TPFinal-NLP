"""Herramientas disponibles para el agente ejecutor."""
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Obtiene el clima actual para una ubicación dada.
    
    Args:
        location: La ubicación para obtener el clima
        
    Returns:
        La información del clima
    """
    # Simulación de datos de clima para diferentes ciudades
    weather_data = {
        "madrid": "Madrid: 22°C, soleado con algunas nubes. Viento suave del oeste a 10 km/h. Humedad: 45%",
        "barcelona": "Barcelona: 25°C, despejado. Viento del este a 15 km/h. Humedad: 60%",
        "valencia": "Valencia: 24°C, parcialmente nublado. Viento del sur a 8 km/h. Humedad: 55%",
        "sevilla": "Sevilla: 28°C, soleado. Viento ligero del suroeste a 5 km/h. Humedad: 40%"
    }
    
    location_lower = location.lower().strip()
    
    # Buscar coincidencias parciales
    for city, weather in weather_data.items():
        if city in location_lower or location_lower in city:
            return weather
    
    # Si no encuentra la ciudad específica, devolver un clima genérico
    return f"{location}: 20°C, condiciones variables. No hay datos específicos disponibles para esta ubicación."
