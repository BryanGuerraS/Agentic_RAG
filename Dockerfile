
---

### 3. **`Dockerfile`**
Este archivo construye una imagen Docker para tu proyecto.

```dockerfile
# Imagen base
FROM python:3.9-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
