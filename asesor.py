"""
Servicio 1 · Asesor de proyecto (área de ciencia de datos).

Entrada:  idea del proyecto, datos disponibles y nivel.
Salida:   plan en texto, diagrama de etapas, cronograma, tabla de riesgos,
          notebook inicial (.ipynb), README.md y enlace «Abrir en Colab».
"""
import os
import tempfile

import gradio as gr
import nbformat
import pandas as pd

import cuaderno
import dibujo
import gemini_cliente as gc
from esquemas import PlanProyecto

INSTRUCCIONES = """Eres un asesor de proyectos de ciencia de datos para estudiantes universitarios
de estadística en Colombia. Responde en español, con lenguaje claro.

Con la idea, los datos y el nivel del estudiante, propone un plan realista:
- Una pregunta de investigación concreta y medible.
- Datos sugeridos sin datos personales identificables; si hacen falta, indica cómo anonimizarlos.
- Una métrica principal y por qué es la adecuada.
- De 4 a 6 etapas cortas (máximo 4 palabras cada una) para el diagrama.
- Un cronograma de 5 a 7 tareas dentro de 8 semanas (semana_inicio de 0 a 7, semanas de 1 a 3).
- De 2 a 4 riesgos éticos, legales o técnicos con su mitigación (menciona la Ley 1581 de 2012 si hay datos personales).
- De 3 a 5 pasos de código Python para un notebook inicial de Colab: carga o simulación de datos,
  exploración, un modelo base y su evaluación. El código debe ejecutarse en Colab sin instalar nada
  adicional; si no hay datos reales, genera datos simulados con numpy.
No inventes cifras ni fuentes.
Escribe con la ortografía completa del español, con tildes y eñes (por ejemplo: predicción, deserción, académico)."""


def _armar_notebook(plan):
    """Convierte el plan en un notebook con celdas de texto y de código."""
    nb = nbformat.v4.new_notebook()
    celdas = [nbformat.v4.new_markdown_cell(
        f"# {plan.titulo}\n\n**Pregunta de investigación:** {plan.pregunta_investigacion}\n\n"
        f"**Objetivo:** {plan.objetivo}\n\n**Métrica principal:** {plan.metrica_principal}\n\n"
        "_Notebook generado por la app Asistente de Datos y Nube. Revise y adapte el código._")]
    for paso in plan.pasos_codigo:
        celdas.append(nbformat.v4.new_markdown_cell(f"## {paso.titulo}\n{paso.explicacion}"))
        celdas.append(nbformat.v4.new_code_cell(paso.codigo))
    nb.cells = celdas
    return nb


def _armar_readme(plan):
    """README.md del proyecto, listo para un repositorio."""
    lineas = [f"# {plan.titulo}", "", f"**Pregunta:** {plan.pregunta_investigacion}", "",
              f"**Objetivo:** {plan.objetivo}", "", "## Datos"]
    lineas += [f"- {d}" for d in plan.datos_sugeridos]
    lineas += ["", f"## Métrica\n{plan.metrica_principal}: {plan.justificacion_metrica}", "", "## Etapas"]
    lineas += [f"{i}. {e}" for i, e in enumerate(plan.etapas, 1)]
    lineas += ["", "## Riesgos"] + [f"- **{r.riesgo}:** {r.mitigacion}" for r in plan.riesgos]
    lineas += ["", "## Librerías", ", ".join(plan.librerias)]
    ruta = os.path.join(tempfile.mkdtemp(), "README.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    return ruta


def _texto_plan(plan):
    datos = "\n".join(f"- {d}" for d in plan.datos_sugeridos)
    return (f"## {plan.titulo}\n**Pregunta de investigación:** {plan.pregunta_investigacion}\n\n"
            f"**Objetivo:** {plan.objetivo}\n\n**Datos sugeridos:**\n{datos}\n\n"
            f"**Métrica principal:** {plan.metrica_principal}. {plan.justificacion_metrica}")


def asesorar(idea, datos, nivel):
    """Pide el plan a Gemini y arma todas las salidas del servicio."""
    vacio = (None,) * 7
    if not idea or not idea.strip():
        return ("✍️ Escriba la idea de su proyecto.",) + vacio[1:]
    prompt = f"Idea: {idea}\nDatos disponibles: {datos or 'no especificados'}\nNivel: {nivel}"
    try:
        r = gc.preguntar(prompt, esquema=PlanProyecto, instrucciones=INSTRUCCIONES)
        plan = r.parsed if isinstance(r.parsed, PlanProyecto) else PlanProyecto.model_validate_json(r.text)
    except Exception as e:
        return (f"❌ No fue posible generar el plan: {e}",) + vacio[1:]

    riesgos = pd.DataFrame([{"Riesgo": x.riesgo, "Mitigación": x.mitigacion} for x in plan.riesgos])
    nb = _armar_notebook(plan)
    nombre = cuaderno.nombre_archivo(plan.titulo)
    ruta_nb = cuaderno.guardar_local(nb, nombre)
    enlace = cuaderno.publicar(nb, "asesor", nombre)
    if enlace:
        colab = f"### [🚀 Abrir el notebook en Colab]({enlace})\nEn Colab: Archivo → Guardar una copia en Drive."
    else:
        colab = "ℹ️ El enlace a Colab no está disponible; descargue el notebook y súbalo a Colab."
    return (_texto_plan(plan), dibujo.diagrama_etapas(plan.etapas), dibujo.cronograma(plan.cronograma),
            riesgos, ruta_nb, _armar_readme(plan), colab)


def construir_pestana():
    """Crea los componentes de la pestaña dentro del gr.Tab que la llama."""
    gr.Markdown("Describa su idea y reciba un plan, un diagrama, un cronograma y un notebook inicial.")
    with gr.Row():
        with gr.Column(scale=1):
            idea = gr.Textbox(label="Idea del proyecto", lines=4,
                              placeholder="Ej.: predecir qué estudiantes de primer semestre tienen riesgo de desertar")
            datos = gr.Textbox(label="Datos disponibles", lines=2,
                               placeholder="Ej.: notas del primer corte, asistencia, programa")
            nivel = gr.Dropdown(["Proyecto de curso", "Trabajo de grado"], value="Proyecto de curso", label="Nivel")
            boton = gr.Button("Asesorar", variant="primary")
        with gr.Column(scale=2):
            plan = gr.Markdown()
            diagrama = gr.Image(label="Etapas del proyecto", type="filepath")
            gantt = gr.Image(label="Cronograma", type="filepath")
            riesgos = gr.Dataframe(label="Riesgos y mitigación", wrap=True, column_widths=["40%", "60%"])
            with gr.Row():
                archivo_nb = gr.File(label="Notebook inicial (.ipynb)")
                archivo_readme = gr.File(label="README.md")
            colab = gr.Markdown()
    boton.click(asesorar, inputs=[idea, datos, nivel],
                outputs=[plan, diagrama, gantt, riesgos, archivo_nb, archivo_readme, colab])
