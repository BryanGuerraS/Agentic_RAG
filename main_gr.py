import time
import os
from typing import List
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
lista_documentos_iniciales = cargar_documentos_en_chroma_db(directory="documents/preprocessed/", persist_directory="chroma_db/preprocessed")

import shutil  # Para manejar correctamente la copia de archivos
def cargar_archivo_nuevo(files, chatbot, rag_with_dropdown):
    """
    Carga nuevos archivos seleccionados en ChromaDB y actualiza la interfaz con un mensaje de confirmación.
    
    Parameters:
        files (List): Lista de archivos subidos.
        chatbot (List): Historial del chatbot para mostrar mensajes.
        rag_with_dropdown (str): Dropdown para seleccionar documentos.
    
    Returns:
        tuple: Estado del chatbot actualizado y lista de archivos cargados.
    """
    try:
        upload_dir = "documents/uploaded/"
        persist_dir = "chroma_db/uploaded/"
        
        # Crear directorio de carga si no existe
        os.makedirs(upload_dir, exist_ok=True)
        
        documentos_subidos = []
        
        # Guardar archivos en el directorio
        for file in files:
            file_name = os.path.basename(file.name)
            file_path = os.path.join(upload_dir, file_name)
            
            # Usar shutil para copiar correctamente el archivo
            with open(file.name, "rb") as src_file:
                with open(file_path, "wb") as dest_file:
                    shutil.copyfileobj(src_file, dest_file)
            
            documentos_subidos.append(file_name)
        
        # Procesar los documentos cargados e indexarlos en ChromaDB
        nuevos_documentos = cargar_documentos_en_chroma_db(
            directory=upload_dir,
            persist_directory=persist_dir
        )
        
        lista_documentos_total = lista_documentos_iniciales + nuevos_documentos

        # Mensaje de éxito en formato de tupla
        chatbot.append(("Cargando documento ...", f"Documento cargado con éxito. Ya puedes hacerle consultas :)"))
        return "", chatbot, gr.Dropdown(choices=lista_documentos_total, value=lista_documentos_total[0])
    except Exception as e:
        # Mensaje de error en formato de tupla
        chatbot.append(("Cargando documento ...", f"Error al cargar documento: {str(e)}"))
        return "", chatbot, gr.Dropdown()

# Función para procesar la consulta
def consultar_llm(question, doc_seleccionado, history):
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

    response = procesar_consulta(state, doc_seleccionado)

    return response["answer"]

# Configurar la interfaz con autenticación
# Configurar la interfaz con autenticación
with gr.Blocks(css="styles.css") as demo:
    with gr.Tabs():
        with gr.TabItem("RAG Tradicional"):
            ### Primera Fila
            with gr.Row() as row_one:
                # Referencias encontradas
                with gr.Column(visible=False) as reference_bar:
                    ref_output = gr.Markdown()
                # Respuesta de chatbot
                with gr.Column() as chatbot_output:
                    chatbot = gr.Chatbot(
                        [],
                        elem_id="chatbot",
                        height=500, 
                        avatar_images=["images/iruma.jpg", "images/openai.png"]
                    )
            ### Segunda Fila | Caja para ingresar el query
            with gr.Row() as row_two:
                input_txt = gr.Textbox(
                    lines=4,
                    scale=8,
                    placeholder="Ingresa un texto y presiona Enter o carga un archivo Word o PDF.",
                    container=False,
                )
            ### Tercera Fila | Caja de botones
            with gr.Row() as row_three:
                text_submit_btn = gr.Button(value="Submit")
                sidebar_state = gr.State(False)
                btn_toggle_sidebar = gr.Button(value="Referencias")
                upload_btn = gr.UploadButton(
                    "📁 Cargar archivos", file_types=[
                        '.pdf',
                        '.docx'
                    ],
                    file_count="multiple")
                temperature_bar = gr.Slider(minimum=0, maximum=1, value=0, step=0.1, scale=0.5, label="Temperatura", info="Escoge entre 0 y 1")
                rag_with_dropdown = gr.Dropdown(label="Selecciona documento:", choices=lista_documentos_iniciales, value=lista_documentos_iniciales[0])
                clear_button = gr.ClearButton([input_txt, chatbot])

                # Procedimientos
                file_msg = upload_btn.upload(
                    fn=cargar_archivo_nuevo, 
                    inputs=[upload_btn, chatbot, rag_with_dropdown], 
                    outputs=[input_txt, chatbot, rag_with_dropdown], 
                    queue=True
                )

                txt_msg = input_txt.submit(
                    fn=consultar_llm,
                    inputs=[chatbot, input_txt, rag_with_dropdown, temperature_bar],
                    outputs=[input_txt,chatbot, ref_output],
                    queue=False
                ).then(
                    lambda: gr.Textbox(interactive=True), None, [input_txt], queue=False
                )

                txt_msg = text_submit_btn.click(
                    fn=procesar_consulta, 
                    inputs=[chatbot, input_txt,rag_with_dropdown, temperature_bar],
                    outputs=[input_txt, chatbot, ref_output],
                    queue=False
                ).then(
                    lambda: gr.Textbox(interactive=True), None, [input_txt], queue=False
                )

demo.launch()