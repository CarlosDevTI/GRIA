#* VERSION SLIM DE PYTHON => ES MAS LIGERA PARA PRODUCION
FROM python:3.11-slim

#* EVITAR QUE PYTHON GENERE ARCHIVOS .pyc Y BUFER EN LA SALIDA
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#* ESTABLECER EL DIRECTORIO DE TRABAJO DENTRO DEL CONTENEDOR
WORKDIR /app

#* COPIAR LAS DEPENDENCIAS
COPY requirements.txt .

# INSTALAR DEPENDENCIAS DEL SISTEMA (PostgreSQL, no MySQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#* COPIAR E INSTALAR LAS DEPENDENCIAS DE PYTHON 
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#* COPIAR TODO EL CODIGO DEL PROYECTO AL DIRECTORIO DE TRABAJO
COPY . .

#* EXPONER EL PUERTO 8002 PARA QUE SEA ACCESIBLE DESDE AFUERA DEL CONTENDOR
EXPOSE 8002

#* COMANDO POR DEFECTO
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]