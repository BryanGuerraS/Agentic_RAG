from app.models import SolicitudConsulta
from app.config import load_env_vars
from app.db import cargar_documento_en_chroma_db
from app.services import procesar_consulta
import gradio as gr

# Función para procesar la consulta
def consultar_llm(user_name, question):
    """
    Procesa la consulta del usuario y devuelve la respuesta.
    
    Parameters:
        user_name (str): Nombre del usuario.
        question (str): Pregunta del usuario.
    
    Returns:
        str: Respuesta generada por el backend.
    """
    state = SolicitudConsulta(
        user_name=user_name,
        question=question
    )
    load_env_vars()
    cargar_documento_en_chroma_db()
    response = procesar_consulta(state)
    return response["answer"]

# Credenciales para autenticación
USERNAME = "admin"  # Cambia esto por el nombre de usuario deseado
PASSWORD = "1234"  # Cambia esto por una contraseña segura

# Configurar la interfaz con autenticación
gr.Interface(
    fn=consultar_llm, 
    inputs=[
        gr.Textbox(label="Tu nombre:", placeholder="Ingresa tu nombre..."),
        gr.Textbox(label="Pregunta:", placeholder="Escribe tu pregunta aquí..."),
    ],
    outputs="text",
    title="Asistente de Consultas",
    description="Haz preguntas y obtén respuestas rápidas y precisas. Escribe tu consulta en el cuadro de texto."
).launch(share=True, auth=(USERNAME, PASSWORD))