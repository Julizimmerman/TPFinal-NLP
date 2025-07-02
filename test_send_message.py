#!/usr/bin/env python3

import sys
import os

# Agregar el directorio del bot al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'plan_and_execute_bot', 'bot'))

from tools.gmail import send_message

def test_send_message():
    """Prueba la función send_message"""
    
    # Datos de prueba
    to = "spourteau@udesa.edu.ar"
    subject = "Resumen Consolidado de Respuestas - Prueba"
    body_html = """
    <h2>Resumen Consolidado de Respuestas</h2>
    <p>Este es un mensaje de prueba para verificar que la función send_message funciona correctamente.</p>
    <ul>
        <li>
            <strong>Remitente:</strong> Santiago Pourteau<br>
            <strong>Asunto:</strong> Futbol Sabado<br>
            <strong>Fecha:</strong> 2 de julio de 2025<br>
            <strong>Resumen:</strong> Santiago recuerda que el sábado jugarán al fútbol con Messi.
        </li>
        <li>
            <strong>Remitente:</strong> Santiago Pourteau<br>
            <strong>Asunto:</strong> Asado Mañana<br>
            <strong>Fecha:</strong> 2 de julio de 2025<br>
            <strong>Resumen:</strong> Santiago menciona que tienen un asado mañana con los de la facultad.
        </li>
    </ul>
    <p>Saludos,<br>Bot de Gmail</p>
    """
    
    print("Enviando mensaje de prueba...")
    result = send_message.invoke({"to": to, "subject": subject, "body_html": body_html})
    print(f"Resultado: {result}")

if __name__ == "__main__":
    test_send_message() 