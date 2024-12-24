"""
Módulo de configuración para cargar y validar variables de entorno.

Este módulo se encarga de cargar las variables de entorno desde un archivo `.env` 
utilizando `python-dotenv` y validar que todas las claves requeridas estén presentes.

Funcionalidades principales:
- Cargar variables de entorno desde un archivo `.env`.
- Validar la existencia de claves de entorno esenciales.
- Lanzar un error si alguna clave obligatoria falta.

Dependencias:
- os: Acceso a variables de entorno del sistema.
- dotenv (load_dotenv): Carga variables de entorno desde un archivo local.
"""

import os
from dotenv import load_dotenv

# Lista de claves de entorno requeridas
REQUIRED_KEYS = [
    "LANGCHAIN_API_KEY",
    "COHERE_API_KEY",
]

def load_env_vars():
    """
    Carga las variables de entorno desde un archivo .env.
    """
    load_dotenv()
    
    # Validar que las claves necesarias estén presentes
    missing_keys = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    
    if missing_keys:
        raise EnvironmentError(f"Faltan las siguientes claves de entorno: {', '.join(missing_keys)}")