import os
import shutil
import gradio as gr
from app.models import SolicitudConsulta
from app.services import procesar_consulta
from app.config import load_env_vars
from app.inicializar_db import inicializar_documentos
from app.cargar_en_chroma_db import cargar_documentos_en_chroma_db
from dotenv import load_dotenv

# Credenciales para autenticación (solo para DEMO)
USERNAME = "admin"  # Nombre de usuario predeterminado
PASSWORD = "1234"  # Contraseña predeterminada

# Carga de Variables de entorno
load_env_vars()

# Carga de documentos iniciales en Preprocessed y Uploaded
lista_documentos_iniciales = inicializar_documentos()

def btn_cargar_archivo_nuevo(files, chatbot, rag_with_dropdown):
    """
    Carga nuevos archivos seleccionados en ChromaDB y actualiza la interfaz con un mensaje de confirmación.
    
    Parameters:
        files (List): Lista de archivos subidos.
        chatbot (List): Historial del chatbot para mostrar mensajes.
        rag_with_dropdown (str): Dropdown para seleccionar documentos.
    
    Returns:
        tuple: Estado del chatbot actualizado y lista de documentos actualizada en el dropdown.
    """
    try:
        # Directorios para almacenar archivos subidos y persistencia en ChromaDB
        upload_dir = "documents/uploaded/"
        persist_dir = "chroma_db/uploaded/"
        
        documentos_cargados = []

        # Guardar cada archivo en el directorio correspondiente
        for file in files:
            file_name = os.path.basename(file.name)
            file_path = os.path.join(upload_dir, file_name)
            shutil.copy2(file.name, file_path) # Copiar el archivo al directorio uploaded
            documentos_cargados.append(file_name)

        # Procesar los documentos cargados e indexarlos en ChromaDB
        nuevos_documentos = cargar_documentos_en_chroma_db(
            directory=upload_dir,
            persist_directory=persist_dir,
            flag_nuevo=True
        )
        
        # Combinar lista de documentos iniciales y nuevos
        lista_documentos_total = lista_documentos_iniciales + nuevos_documentos

        # Actualizar historial del chatbot con mensaje de éxito
        chatbot.append({"role": "user", "content": "Cargando documento..."})
        chatbot.append({"role": "assistant", "content": "Documento cargado con éxito. Ya puedes hacerle consultas :)"})

        # Retornar el estado actualizado
        return "", chatbot, gr.Dropdown(choices=lista_documentos_total, value=lista_documentos_total[-1])
    except Exception as e:
        # Manejo de errores y actualización del chatbot
        chatbot.append({"role": "assistant", "content": f"Error al cargar documento: {str(e)}"})
        return "", chatbot, gr.Dropdown()
    
# Función para procesar la consulta
def consultar_llm(question, doc_seleccionado, history, temperature):
    """
    Procesa la consulta del usuario y devuelve la respuesta generada por el modelo LLM.

    Parameters:
        question (str): Pregunta del usuario.
        doc_seleccionado (str): Documento seleccionado en el dropdown.
        history (List): Historial de interacciones del chatbot.
        temperature (float): Valor de temperatura para la generación de texto.

    Returns:
        tuple: Historial actualizado y texto de la consulta enviada.
    """
    # Crear instancia de la solicitud de consulta
    state = SolicitudConsulta(
        user_name=USERNAME,
        question=str(question)
    )

    # Procesar la consulta utilizando el servicio configurado
    response = procesar_consulta(state, doc_seleccionado, temperature)

    # Actualizar el historial con el rol de usuario y asistente
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response["answer"]})
    
    return history, ""

# Interfaz
with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("RAG Tradicional"):
            # Primera fila: salida del chatbot
            with gr.Row() as row_one:
                with gr.Column() as chatbot_output:
                    chatbot = gr.Chatbot(
                        [],
                        elem_id="chatbot",
                        height=500, 
                        avatar_images=["images/iruma.jpg", "images/openai.png"],
                        type="messages"
                    )
            # Segunda fila: caja de texto para ingresar consultas
            with gr.Row() as row_two:
                input_txt = gr.Textbox(
                    lines=4,
                    scale=8,
                    placeholder="Ingresa un texto y presiona Shift + Enter para hacer consultas. También puedes cargartu propio archivo Word o PDF :)",
                    container=False,
                    submit_btn=True
                )
            # Tercera fila: botones y controles adicionales
            with gr.Row() as row_three:
                text_submit_btn = gr.Button(value="Submit")
                sidebar_state = gr.State(False)
                upload_btn = gr.UploadButton(
                    "📁 Cargar archivos", file_types=[
                        '.pdf',
                        '.docx'
                    ],
                    file_count="multiple")
                temperature_bar = gr.Slider(minimum=0, maximum=1, value=0, step=0.1, scale=1, label="Temperatura", info="Escoge entre 0 y 1")
                rag_with_dropdown = gr.Dropdown(label="Selecciona documento:", scale=2, choices=lista_documentos_iniciales, value=lista_documentos_iniciales[0])
                clear_button = gr.ClearButton([input_txt, chatbot])

                # Configuración de eventos de botones
                file_msg = upload_btn.upload(
                    fn=btn_cargar_archivo_nuevo, 
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

# Lanzar la aplicación con autenticación
# La opción `share=True` permite compartir la aplicación públicamente durante su ejecución
# NOTA: No se usarán credenciales planas en producción

demo.launch(
    share=True,
    #auth=[(USERNAME, PASSWORD)] # Si se prende la autenticación entonces el link público no funcionará
)