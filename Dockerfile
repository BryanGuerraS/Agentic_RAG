# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt /app/

# Instala las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos los archivos del proyecto al contenedor
COPY . /app/

# Expón el puerto en el que se ejecutará la aplicación
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Comando para ejecutar la aplicación usando Uvicorn
CMD ["python", "main.py"]
