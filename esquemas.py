"""
Esquemas de respuesta (Pydantic) que se le piden a Gemini.

Gemini no responde texto libre: llena estos campos en formato JSON.
Así la app puede dibujar, armar tablas y crear archivos sin adivinar.
"""
from pydantic import BaseModel


# ---------- Servicio: Asesor de proyecto ----------

class Tarea(BaseModel):
    tarea: str            # nombre corto de la tarea
    semana_inicio: int    # semana en que empieza (0 a 7)
    semanas: int          # cuántas semanas dura (1 a 3)


class Riesgo(BaseModel):
    riesgo: str
    mitigacion: str


class PasoCodigo(BaseModel):
    titulo: str           # título de la sección del notebook
    explicacion: str      # qué hace el código, en una o dos frases
    codigo: str           # código Python ejecutable en Colab


class PlanProyecto(BaseModel):
    titulo: str
    pregunta_investigacion: str
    objetivo: str
    datos_sugeridos: list[str]
    metrica_principal: str
    justificacion_metrica: str
    etapas: list[str]               # de 4 a 6 etapas del flujo de trabajo
    cronograma: list[Tarea]         # de 5 a 7 tareas en 8 semanas
    riesgos: list[Riesgo]           # de 2 a 4 riesgos éticos, legales o técnicos
    librerias: list[str]            # librerías de Python sugeridas
    pasos_codigo: list[PasoCodigo]  # de 3 a 5 celdas para el notebook inicial
