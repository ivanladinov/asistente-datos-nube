"""
Crea notebooks (.ipynb) y los publica en el repositorio de cuadernos para abrirlos en Colab.

Variables de entorno:
    GITHUB_TOKEN            token de grano fino con Contents (Read and write) solo en el repo de cuadernos
    GITHUB_USUARIO          usuario de GitHub dueño del repositorio
    GITHUB_REPO_CUADERNOS   nombre del repositorio de cuadernos (por defecto: asistente-cuadernos)
"""
import base64
import datetime
import os
import re
import tempfile
import unicodedata

import nbformat
import requests


def nombre_archivo(titulo):
    """Convierte un título en un nombre de archivo seguro, con fecha y hora."""
    sin_tildes = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-z0-9]+", "-", sin_tildes.lower()).strip("-")[:40] or "proyecto"
    return f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{base}.ipynb"


def guardar_local(nb, nombre):
    """Guarda el notebook en una carpeta temporal y devuelve la ruta (para descargarlo)."""
    ruta = os.path.join(tempfile.mkdtemp(), nombre)
    nbformat.write(nb, ruta)
    return ruta


def publicar(nb, carpeta, nombre):
    """
    Sube el notebook a GitHub y devuelve el enlace para abrirlo en Colab.
    Devuelve None si no hay token configurado o si GitHub rechaza la subida.
    """
    token = os.environ.get("GITHUB_TOKEN")
    usuario = os.environ.get("GITHUB_USUARIO")
    repo = os.environ.get("GITHUB_REPO_CUADERNOS", "asistente-cuadernos")
    if not token or not usuario:
        return None
    ruta = f"{carpeta}/{nombre}"
    contenido = base64.b64encode(nbformat.writes(nb).encode("utf-8")).decode("ascii")
    try:
        r = requests.put(
            f"https://api.github.com/repos/{usuario}/{repo}/contents/{ruta}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            json={"message": f"Notebook generado por la app: {nombre}", "content": contenido},
            timeout=30,
        )
    except requests.RequestException:
        return None
    if r.status_code != 201:
        return None
    return f"https://colab.research.google.com/github/{usuario}/{repo}/blob/main/{ruta}"
