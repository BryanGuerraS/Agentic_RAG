import time
import os
from typing import List
from app.models import SolicitudConsulta
from app.config import load_env_vars
from app.cargar_en_chroma_db import cargar_documentos_en_chroma_db
from app.services import procesar_consulta
import gradio as gr
import shutil  # Para manejar correctamente la copia de archivos

# Credenciales para autenticación
USERNAME = "admin"  # Solo para DEMO
PASSWORD = "1234"  # Solo para DEMO

# Cargar Variables de Entorno
load_env_vars()

# Inicialización de documentos combinados
def inicializar_documentos():
    """
    Carga los documentos precargados y los previamente subidos.
    """
    preprocessed_dir = "documents/preprocessed/"
    uploaded_dir = "documents/uploaded/"
    persist_preprocessed = "chroma_db/preprocessed/"
    persist_uploaded = "chroma_db/uploaded/"

    # Cargar documentos desde las carpetas predefinidas
    documentos_preprocesados = cargar_documentos_en_chroma_db(
        directory=preprocessed_dir,
        persist_directory=persist_preprocessed,
        flag_nuevo=False
    )

    documentos_cargados = cargar_documentos_en_chroma_db(
        directory=uploaded_dir,
        persist_directory=persist_uploaded,
        flag_nuevo=False
    )

    # Combinar ambas listas y devolver
    return documentos_preprocesados + documentos_cargados

# Lista inicial global de documentos
lista_documentos_iniciales = inicializar_documentos()


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
        
        documentos_cargados = []
        # Mensaje de carga del usuario 
        chatbot.append({"role": "user", "content": "Cargando documento..."})

        # Guardar archivos en el directorio
        for file in files:
            file_name = os.path.basename(file.name)
            file_path = os.path.join(upload_dir, file_name)
            
            # Usar shutil para copiar correctamente el archivo
            with open(file.name, "rb") as src_file:
                with open(file_path, "wb") as dest_file:
                    shutil.copyfileobj(src_file, dest_file)
            
            documentos_cargados.append(file_name)
        
        # Procesar los documentos cargados e indexarlos en ChromaDB
        nuevos_documentos = cargar_documentos_en_chroma_db(
            directory=upload_dir,
            persist_directory=persist_dir,
            flag_nuevo=True
        )
        
        lista_documentos_total = lista_documentos_iniciales + nuevos_documentos

        # Mensaje de éxito en formato de tupla
        chatbot.append({"role": "assistant", "content": "Documento cargado con éxito. Ya puedes hacerle consultas :)"})
        return "", chatbot, gr.Dropdown(choices=lista_documentos_total, value=lista_documentos_total[0])
    except Exception as e:
        # Mensaje de error en formato de tupla
        chatbot.append({"role": "assistant", "content": f"Error al cargar documento: {str(e)}"})
        return "", chatbot, gr.Dropdown()

# Función para procesar la consulta
def consultar_llm(question, doc_seleccionado, history, temperature):
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

    response = procesar_consulta(state, doc_seleccionado, temperature)

    # Formatear la historia con 'role' y 'content' 
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response["answer"]})
    
    return history, question

# Interfaz
with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("RAG Tradicional"):
            ### Primera Fila
            with gr.Row() as row_one:
                # Referencias encontradas
                # with gr.Column(visible=False) as reference_bar:
                #    ref_output = gr.Markdown()
                # Respuesta de chatbot
                with gr.Column() as chatbot_output:
                    chatbot = gr.Chatbot(
                        [],
                        elem_id="chatbot",
                        height=500, 
                        avatar_images=["images/iruma.jpg", "images/openai.png"],
                        type="messages"
                    )
            ### Segunda Fila | Caja para ingresar el query
            with gr.Row() as row_two:
                input_txt = gr.Textbox(
                    lines=4,
                    scale=8,
                    placeholder="Ingresa un texto y clickea Submit o carga un archivo Word o PDF.",
                    container=False,
                    interactive=True
                )
            ### Tercera Fila | Caja de botones
            with gr.Row() as row_three:
                text_submit_btn = gr.Button(value="Submit")
                sidebar_state = gr.State(False)
                #btn_toggle_sidebar = gr.Button(value="Referencias")
                upload_btn = gr.UploadButton(
                    "📁 Cargar archivos", file_types=[
                        '.pdf',
                        '.docx'
                    ],
                    file_count="multiple")
                temperature_bar = gr.Slider(minimum=0, maximum=1, value=0, step=0.1, scale=1, label="Temperatura", info="Escoge entre 0 y 1")
                rag_with_dropdown = gr.Dropdown(label="Selecciona documento:", scale=2, choices=lista_documentos_iniciales, value=lista_documentos_iniciales[0])
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
                    inputs=[input_txt, rag_with_dropdown, chatbot, temperature_bar],
                    outputs=[chatbot, input_txt],
                    queue=False
                )

                text_submit_btn.click(
                    fn=consultar_llm,
                    inputs=[input_txt, rag_with_dropdown, chatbot, temperature_bar],
                    outputs=[chatbot, input_txt],
                    queue=False
                ).then(
                    lambda: gr.Textbox(interactive=True), None, [input_txt], queue=False
                )

demo.launch(
    share=False,
    auth=[(USERNAME, PASSWORD)]
)