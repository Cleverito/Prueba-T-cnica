FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias primero (capa cacheada por Docker si requirements.txt no cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear carpeta para logos (archivos estáticos subidos)
RUN mkdir -p /app/static/logos

# Puerto que expone el backend
EXPOSE 8000

# Comando por defecto (sobreescrito por docker-compose en desarrollo para añadir --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
