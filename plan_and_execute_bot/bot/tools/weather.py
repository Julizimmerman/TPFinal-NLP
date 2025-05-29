import os
import requests
from datetime import datetime
from collections import defaultdict
from langchain.tools import tool


API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL_CURRENT  = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
BASE_URL_GEOCODE  = "http://api.openweathermap.org/geo/1.0/direct"
BASE_URL_AIRQ     = "http://api.openweathermap.org/data/2.5/air_pollution"

@tool
def get_weather(location: str) -> str:
    """Clima actual (descr, temp, humedad)."""
    params = {"q": location, "appid": API_KEY, "units": "metric", "lang": "es"}
    resp = requests.get(BASE_URL_CURRENT, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error al obtener el clima: {data.get('message','desconocido')}"
    w = data["weather"][0]
    m = data["main"]
    return (f"En {location}: {w['description']}, "
            f"{m['temp']}°C, humedad {m['humidity']}%.")

@tool
def get_next_rain_day(location: str) -> str:
    """Primer día con lluvia en los próximos 5 días."""
    params = {"q": location, "appid": API_KEY, "units": "metric", "lang": "es"}
    resp = requests.get(BASE_URL_FORECAST, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error al obtener el pronóstico: {data.get('message','desconocido')}"
    seen = set()
    for e in data["list"]:
        day = e["dt_txt"].split()[0]
        if day in seen: continue
        seen.add(day)
        main = e["weather"][0]["main"].lower()
        if "rain" in main:
            fecha = datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m/%Y")
            print(f"El próximo día con lluvia en {location} será el {fecha}.")
            return fecha
    
    print(f"No se espera lluvia en los próximos 5 días en {location}.")
    return None

@tool
def geocode(location: str) -> tuple[float,float] | None:
    """Devuelve (lat, lon) o None si falla."""
    params = {"q": location, "limit":1, "appid": API_KEY}
    resp = requests.get(BASE_URL_GEOCODE, params=params)
    arr = resp.json()
    if not arr: return None
    return arr[0]["lat"], arr[0]["lon"]

@tool
def get_air_quality(location: str) -> str:
    """Índice de calidad del aire (AQI) actual."""
    coords = geocode(location)
    if not coords:
        return f"No pude geolocalizar {location}."
    lat, lon = coords
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    resp = requests.get(BASE_URL_AIRQ, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error AQI: {data.get('message','desconocido')}"
    # AQI: 1=Bueno, 2=Moderado, 3=Dañino moderado, 4=Dañino, 5=Peligroso
    aqi = data["list"][0]["main"]["aqi"]
    etiquetas = {1:"Bueno", 2:"Moderado", 3:"Dañino para grupos sensibles",
                 4:"Dañino", 5:"Muy peligroso"}
    return f"Calidad del aire en {location}: {etiquetas.get(aqi, aqi)} (AQI={aqi})."

@tool
def get_sun_times(location: str) -> str:
    """Salida y puesta de sol para hoy."""
    params = {"q": location, "appid": API_KEY}
    resp = requests.get(BASE_URL_CURRENT, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error al obtener sol: {data.get('message','desconocido')}"
    off = data["timezone"]             # en segundos
    sr = data["sys"]["sunrise"] + off
    ss = data["sys"]["sunset"]  + off
    fmt = lambda ts: datetime.utcfromtimestamp(ts).strftime("%H:%M")
    return (f"En {location} hoy sale el sol a las {fmt(sr)} y "
            f"se pone a las {fmt(ss)} (hora local).")

@tool
def get_weekly_summary(location: str) -> str:
    """Min/Max diarios de los próximos 5 días."""
    params = {"q": location, "appid": API_KEY, "units": "metric"}
    resp = requests.get(BASE_URL_FORECAST, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error resumen: {data.get('message','desconocido')}"
    temps = defaultdict(lambda: {"min": float("inf"), "max": float("-inf")})
    for e in data["list"]:
        day = e["dt_txt"].split()[0]
        t = e["main"]["temp"]
        temps[day]["min"] = min(temps[day]["min"], t)
        temps[day]["max"] = max(temps[day]["max"], t)
    líneas = []
    for day, v in temps.items():
        fecha = datetime.strptime(day, "%Y-%m-%d").strftime("%d/%m")
        líneas.append(f"{fecha}: {v['min']}–{v['max']}°C")
    return "Resumen 5 días: " + "; ".join(líneas)

@tool
def get_clothing_advice(location: str) -> str:
    """Recomendación de ropa según el clima actual."""
    params = {"q": location, "appid": API_KEY, "units": "metric", "lang":"es"}
    resp = requests.get(BASE_URL_CURRENT, params=params)
    data = resp.json()
    if resp.status_code != 200:
        return f"Error ropa: {data.get('message','desconocido')}"
    t = data["main"]["temp"]
    desc = data["weather"][0]["main"].lower()
    consejo = []
    if t < 10:
        consejo.append("abrígate con abrigo y bufanda")
    elif t < 20:
        consejo.append("lleva una chaqueta o suéter")
    else:
        consejo.append("ropa ligera está bien")
    if "rain" in desc:
        consejo.append("no olvides un paraguas")
    return "Recomendación: " + " y ".join(consejo) + "."


