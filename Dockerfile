# Imagen base liviana con Python 3.11
FROM python:3.11-slim

# Sin archivos .pyc y con los mensajes de Python visibles de inmediato en los registros de Render
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero solo las dependencias: Docker reutiliza esta capa si solo cambia el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después, el código de la app
COPY . .

# Buena práctica: ejecutar con un usuario sin privilegios
RUN useradd --create-home appuser
USER appuser

# Puerto por defecto; Render lo reemplaza con la variable PORT
EXPOSE 7860
CMD ["python", "app.py"]
