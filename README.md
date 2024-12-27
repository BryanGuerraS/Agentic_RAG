# 🚀 RAG Tradicional con Langchain y Gradio🌟
¡Bienvenido al proyecto! 🎉 Este repositorio contiene una implementación de una API que utiliza Gradio para procesar preguntas, buscar texto relevante y generar respuestas utilizando un modelo de lenguaje grande (LLM). La aplicación se integra con Cohere para la generación de embeddings y ChromaDB para la búsqueda de similitudes.

## 🧠 Principales Insights o Mejoras del Proyecto
- **Manejo de API Keys en archivo ".env"**: La gestión de las claves de API se realiza de manera segura a través de un archivo `.env`.
- **Framework de Llama Index y OpenAI para análisis de Chunk Size Ideal**: Se implementó el framework de Llama Index junto con OpenAI para ajustar el tamaño óptimo de los fragmentos (chunks) para la búsqueda de información.
- **Framework de Langchain y Cohere para el procesamiento de consultas**: Se utiliza Langchain y Cohere para el procesamiento avanzado de consultas.
- **Actualización del splitter de tamaño fijo a recursivo adicional al overlap**: Se mejoró la forma en que se dividen los documentos, implementando un splitter recursivo con un solapamiento adicional.
- **Actualización del flujo de trabajo para detectar el idioma y responder en el mismo**: Ahora la API detecta el idioma de las preguntas y responde en el mismo idioma.


## 🌟 Características principales
- 🗂️ Procesamiento de documentos `.docx` y `.pdf` para extraer información relevante.  
- 🔍 Almacenamiento de embeddings en **ChromaDB** para búsqueda eficiente de similitudes.  
- 🤖 Respuestas concisas y personalizadas generadas con modelos LLM.  
- 📦 Despliegue simplificado con Docker.  


## 📂 Estructura del proyecto
```console
📁 app  
├── cargar_en_chroma_db.py  # Carga y almacenamiento de documentos en ChromaDB.
├── config.py               # Gestión y validación de variables de entorno.
├── inicializar_db.py       # Inicialización y combinación de documentos preprocesados.
├── models.py               # Definición de los modelos de datos.
📁 documents
├── preprocessed/           # Documentos ya procesados.
├── uploaded/               # Documentos cargados por el usuario.
📁 chroma_db
├── preprocessed/           # Base de datos de embeddings para documentos preprocesados.
├── uploaded/               # Base de datos de embeddings para documentos cargados.
Dockerfile                  # Configuración para construir la imagen Docker.
main.py                     # Archivo principal de la aplicación.
requirements.txt            # Librerías requeridas.
```

## 🚀 Cómo ejecutar el proyecto
### 1️⃣ Requisitos previos
- 🐍 Python 3.9+  
- 🐳 Docker instalado.  
- 🧪 Postman o cualquier cliente HTTP para probar la API.

### 2️⃣ Ejecución local
1. Clona el repositorio:
```console
git clone https://github.com/BryanGuerraS/Traditional-RAG-with-Gradio-Upload-Files.git
cd Traditional-RAG-with-Gradio-Upload-Files
```
2. Crea un entorno virtual e instala las dependencias:
```console
python -m venv env
source env/bin/activate  # En Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Crea un archivo .env en la raíz del proyecto con las siguientes claves:
```console
LANGCHAIN_API_KEY=tu_clave_aqui
COHERE_API_KEY=tu_clave_aqui
```

4. Inicia la API
```console
uvicorn main:app --reload
```
5. Prueba la API
Prueba la API en: http://127.0.0.1:7860/

### 3️⃣ Ejecución con Docker
1. Construye la imagen Docker:
```console
docker build -t rag_gradio .
```
2. Ejecuta el contenedor:
```console
docker run -p 8000:8000 rag_gradio
```
3. Prueba la API:
- La API estará disponible en: http://127.0.0.1:7860/


## 🛠️ Endpoints principales
### Principales preguntas:
- Procesa una pregunta y genera una respuesta basada en documentos relevantes.


```

## 📖 Documentación adicional
- Docker: Este proyecto incluye un archivo Dockerfile que permite desplegar la API rápidamente en un contenedor.
- Módulos separados: Código modular y bien documentado para facilitar su mantenimiento y escalabilidad.

## 🌍 Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras un problema o deseas agregar una mejora, por favor abre un issue o envía un pull request. 🙌