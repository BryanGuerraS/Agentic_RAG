from app.cargar_en_chroma_db import cargar_documentos_en_chroma_db

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