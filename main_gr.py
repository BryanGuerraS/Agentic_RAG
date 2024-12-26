import time
from app.models import SolicitudConsulta
from app.config import load_env_vars
from app.cargar_en_chroma_db import cargar_documentos_en_chroma_db
from app.services import procesar_consulta
import gradio as gr

# Credenciales para autenticación
USERNAME = "admin"  # Solo para DEMO
PASSWORD = "1234"  # Solo para DEMO

# Cargar Variables de Entorno
load_env_vars()

# Cargar data inicial
cargar_documentos_en_chroma_db("documents_preprocessed/")

# Función para procesar la consulta
def consultar_llm(question, history):
    """
    Procesa la consulta del usuario y devuelve la respuesta.
    
    Parameters:
        user_name (str): Nombre del usuario.
        question (str): Pregunta del usuario.
    
    Returns:
        str: Respuesta generada por el backend.
    """
    state = SolicitudConsulta(
        user_name=USERNAME,
        question=str(question)
    )

    response = procesar_consulta(state)

    return response["answer"]

# Configurar la interfaz con autenticación
gr.ChatInterface(
    consultar_llm, 
    type="messages",
    title="Asistente de Consultas de Documentos",
    description="Hazme cualquier pregunta",
    theme="ocean",
    autofocus=False
).launch(
    #share=True, 
    #auth=(USERNAME, PASSWORD)
)