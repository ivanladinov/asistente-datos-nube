"""
Asistente de Datos y Nube: aplicación web multiservicio.

Área de ciencia de datos:      Asesor de proyecto, Analista de CSV.
Área de nube y contenedores:   Asistente de Docker, Arquitecto en la nube, Tutor de la nube.

Cada servicio vive en su propio archivo y aporta su pestaña con construir_pestana().
Los servicios se agregan uno por uno en los pasos del laboratorio.
"""
import os
import gradio as gr

import gemini_cliente as gc
import asesor

# Servicios ya construidos: nombre de la pestaña -> función que arma su contenido
CONSTRUIDOS = {
    "💡 Asesor de proyecto": asesor.construir_pestana,
}

SERVICIOS = {
    "Ciencia de datos": [
        ("💡 Asesor de proyecto", "Plan, diagrama, cronograma y notebook para Colab a partir de una idea."),
        ("📊 Analista de CSV", "Gráficos, hallazgos y el código usado sobre un archivo propio."),
    ],
    "Nube y contenedores": [
        ("🐳 Asistente de Docker", "Genera y revisa Dockerfile y docker-compose.yml, con diagrama de capas."),
        ("🏗️ Arquitecto en la nube", "Diagrama de la solución y equivalentes en Google Cloud, AWS y Azure."),
        ("🎓 Tutor de la nube", "Explica los temas del curso con diagramas y un quiz corto."),
    ],
}


def texto_inicio():
    """Arma el texto de la pestaña Inicio con las dos áreas y sus servicios."""
    partes = ["## ¿En qué le ayudo hoy?\nElija un servicio en las pestañas de arriba."]
    for area, servicios in SERVICIOS.items():
        partes.append(f"### {area}")
        partes += [f"- **{nombre}:** {descripcion}" for nombre, descripcion in servicios]
    return "\n".join(partes)


def estado_cuota():
    return f"**Cuota de hoy:** quedan {gc.consultas_restantes()} de {gc.LIMITE_DIARIO} consultas."


def probar_conexion():
    """Hace una consulta corta a Gemini para verificar la clave y el modelo."""
    try:
        r = gc.preguntar("Responde en una sola frase: ¿qué es la computación en la nube?")
        return "✅ Conexión correcta. Gemini respondió:\n" + r.text, estado_cuota()
    except Exception as e:
        return f"❌ No fue posible conectar con Gemini: {e}", estado_cuota()


with gr.Blocks(title="Asistente de Datos y Nube") as demo:
    gr.Markdown("# ☁️ Asistente de Datos y Nube\n"
                "Computación en la Nube · Facultad de Estadística, Universidad Santo Tomás")

    with gr.Tabs():
        with gr.Tab("Inicio"):
            gr.Markdown(texto_inicio())
            cuota = gr.Markdown(estado_cuota())
            boton_prueba = gr.Button("Probar conexión con Gemini", variant="primary")
            salida_prueba = gr.Textbox(label="Resultado de la prueba", lines=4)
            boton_prueba.click(probar_conexion, outputs=[salida_prueba, cuota])

        for area in SERVICIOS.values():
            for nombre, _ in area:
                with gr.Tab(nombre):
                    if nombre in CONSTRUIDOS:
                        CONSTRUIDOS[nombre]()
                    else:
                        gr.Markdown("🚧 Servicio en construcción. Se agrega en los próximos pasos.")

    gr.Markdown("⚠️ No suba datos personales: en la capa gratuita de Gemini, "
                "Google puede usar las consultas para mejorar sus productos.")
    demo.load(estado_cuota, outputs=cuota)      # actualiza la cuota al abrir la página


if __name__ == "__main__":
    # Render asigna el puerto en la variable PORT; en el computador se usa 7860.
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", "7860")))
