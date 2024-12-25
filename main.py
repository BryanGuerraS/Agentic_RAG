""" 
Módulo principal para inicializar y ejecutar la API de FastAPI.

Estructura del módulo:
1. Importaciones de librerías y módulos necesarios.
2. Inicialización de la aplicación FastAPI.
3. Configuración de eventos de inicio (startup) para preparar recursos como base de datos.
4. Endpoints:
    - GET / : Mensaje de bienvenida.
    - GET /consulta/ : Mensaje indicando el uso de POST.
    - POST /consulta/ : Procesamiento de una consulta enviada por el usuario.

Módulos externos utilizados:
- SolicitudConsulta (modelo de datos).
- load_env_vars (carga de variables de entorno).
- cargar_documento_en_chroma_db (gestión de base de datos de vectores).
- procesar_consulta (procesamiento de consultas).
"""

from fastapi import FastAPI
from app.models import SolicitudConsulta
from app.config import load_env_vars
from app.db import cargar_documento_en_chroma_db
from app.services import procesar_consulta

# Inicializar la aplicación FastAPI
app = FastAPI()

@app.on_event("startup")
def startup_event():
    """
    Validar claves y procesar documento al iniciar el servidor.
    """
    load_env_vars()
    cargar_documento_en_chroma_db()

@app.get("/")
async def root():
    """
    Muestra un mensaje de bienvenida cuando se accede a la raíz de la API.
    """
    return {
        "message": "¡Bienvenido a la API de consultas! Utiliza el endpoint /consulta/ para hacer preguntas."
    }

@app.get("/consulta/")
async def consulta_info():
    """
    Muestra un mensaje indicando que se debe usar POST para realizar consultas.
    """
    return {
        "message": "Este endpoint está diseñado para solicitudes POST. Envía tu consulta como JSON."
    }

@app.post("/consulta/")
async def consulta(state: SolicitudConsulta):
    """
    Procesa las solicitudes de consulta enviadas mediante POST.
    """
    return procesar_consulta(state)