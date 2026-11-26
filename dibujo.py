"""
Funciones de dibujo: convierten los datos que devuelve Gemini en imágenes PNG.

Regla de diseño de la app: Gemini describe y la app dibuja.
"""
import tempfile
import textwrap

import matplotlib
matplotlib.use("Agg")                 # dibuja sin pantalla (servidor)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

COLORES = ["#17877B", "#4F5FB8", "#F2A93B", "#6B7A89", "#C8443F", "#2E8B57", "#0E2A3A"]


def _guardar(fig):
    """Guarda la figura en un PNG temporal y devuelve su ruta."""
    archivo = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    fig.savefig(archivo.name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return archivo.name


def diagrama_etapas(etapas):
    """Dibuja las etapas del proyecto como cajas unidas por flechas, de izquierda a derecha."""
    n = len(etapas)
    fig, ax = plt.subplots(figsize=(2.6 * n, 2.2))
    ax.set_xlim(0, 3 * n)
    ax.set_ylim(0, 2)
    ax.axis("off")
    for i, etapa in enumerate(etapas):
        x = i * 3 + 0.2
        ax.add_patch(FancyBboxPatch((x, 0.45), 2.4, 1.1, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=COLORES[i % len(COLORES)], ec="none", alpha=0.9))
        ax.text(x + 1.2, 1.0, "\n".join(textwrap.wrap(etapa, 14)), ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
        if i < n - 1:
            ax.annotate("", xy=(x + 2.95, 1.0), xytext=(x + 2.45, 1.0),
                        arrowprops=dict(arrowstyle="-|>", color="#6B7A89", lw=1.8))
    return _guardar(fig)


def cronograma(tareas):
    """Dibuja un diagrama de Gantt con las tareas y sus semanas."""
    fig, ax = plt.subplots(figsize=(8, 0.75 * len(tareas) + 1.2))
    for i, t in enumerate(tareas):
        inicio = max(0, min(int(t.semana_inicio), 7))
        duracion = max(1, min(int(t.semanas), 8 - inicio))
        ax.barh(i, duracion, left=inicio, color=COLORES[i % len(COLORES)], height=0.55)
    ax.set_yticks(range(len(tareas)), [textwrap.fill(textwrap.shorten(t.tarea, 60), 30) for t in tareas])
    ax.invert_yaxis()
    ax.set_xticks(range(0, 9), [f"S{k}" for k in range(0, 9)])
    ax.set_xlim(0, 8)
    ax.grid(axis="x", color="#E3E8EC")
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title("Cronograma sugerido · 8 semanas", loc="left", fontweight="bold")
    return _guardar(fig)
