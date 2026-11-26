"""
Cliente de Gemini compartido por todos los servicios de la app.

- Lee la clave de la variable de entorno GEMINI_API_KEY (nunca va en el código).
- Usa el modelo gratuito gemini-3.5-flash-lite (se puede cambiar con GEMINI_MODELO).
- Lleva un contador diario de consultas para no agotar la capa gratuita.
"""
import os
import datetime
import threading

from google import genai
from google.genai import types

MODELO = os.environ.get("GEMINI_MODELO", "gemini-3.5-flash-lite")
LIMITE_DIARIO = int(os.environ.get("LIMITE_DIARIO", "50"))   # consultas por día para toda la app

_cliente = None                        # se crea la primera vez que se usa
_bloqueo = threading.Lock()            # evita errores si dos personas consultan a la vez
_contador = {"fecha": None, "usadas": 0}


def _obtener_cliente():
    """Crea el cliente de Gemini una sola vez, con la clave del entorno."""
    global _cliente
    if _cliente is None:
        clave = os.environ.get("GEMINI_API_KEY")
        if not clave:
            raise RuntimeError("Falta la variable de entorno GEMINI_API_KEY.")
        _cliente = genai.Client(api_key=clave)
    return _cliente


def _reiniciar_si_cambio_el_dia():
    hoy = datetime.date.today()
    if _contador["fecha"] != hoy:
        _contador["fecha"] = hoy
        _contador["usadas"] = 0


def consultas_restantes():
    """Cuántas consultas le quedan hoy a la app."""
    with _bloqueo:
        _reiniciar_si_cambio_el_dia()
        return max(LIMITE_DIARIO - _contador["usadas"], 0)


def preguntar(contenido, esquema=None, ejecutar_codigo=False):
    """
    Envía una consulta a Gemini y devuelve la respuesta completa.

    contenido:        texto del prompt, o una lista con texto y archivos.
    esquema:          clase de Pydantic; si se da, Gemini responde un JSON con esos campos.
    ejecutar_codigo:  si es True, Gemini puede escribir y ejecutar Python (gráficos).
    """
    with _bloqueo:
        _reiniciar_si_cambio_el_dia()
        if _contador["usadas"] >= LIMITE_DIARIO:
            raise RuntimeError("Se agotó la cuota diaria de la app. Intenta de nuevo mañana.")
        _contador["usadas"] += 1

    opciones = {}
    if esquema is not None:
        opciones["response_mime_type"] = "application/json"
        opciones["response_schema"] = esquema
    if ejecutar_codigo:
        opciones["tools"] = [types.Tool(code_execution=types.ToolCodeExecution())]

    configuracion = types.GenerateContentConfig(**opciones) if opciones else None
    return _obtener_cliente().models.generate_content(
        model=MODELO, contents=contenido, config=configuracion
    )
