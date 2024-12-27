import os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

def cargar_documentos_en_chroma_db(directory, persist_directory, flag_nuevo):
    """
    Carga documentos desde un directorio en ChromaDB, dividiéndolos en fragmentos,
    generando embeddings y almacenándolos en una base de vectores.
    
    Parameters:
        directory (str): Ruta del directorio donde se encuentran los documentos a cargar.
        persist_directory (str): Ruta del directorio de persistencia para la base de vectores.
        flag_nuevo (bool): Si es True, solo procesa documentos nuevos no cargados previamente.

    Returns:
        list: Lista con los nombres de los documentos cargados.

    Raises:
        FileNotFoundError: Si el directorio especificado no existe.
    """

    # Validar la existencia del directorio
    if not os.path.exists(directory):
        raise FileNotFoundError(f"El directorio '{directory}' no existe.")
    
    # Inicializar variables y estructuras
    lista_documentos = []
    documentos_ya_cargados = set()
    contador_doc = 0

    # Inicializar Chroma
    vector_store = Chroma(
        collection_name="documentos", 
        embedding_function=CohereEmbeddings(model="embed-multilingual-v2.0"), 
        persist_directory=persist_directory
    )
    
    # Obtener los metadatos de los documentos ya cargados
    for doc in vector_store.get()['metadatas']: 
        documentos_ya_cargados.add(doc['document'])
    print("Documentos ya cargados:", documentos_ya_cargados)

    # Iterar sobre los archivos en el directorio especificado
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Determinar el tipo de documento (PDF o Word) y cargarlo
        if filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            print(f"Formato no soportado: {filename}")
            continue

        # Verificar si el documento ya está cargado y procesar según flag_nuevo
        if filename in documentos_ya_cargados: 
            if flag_nuevo == False:
                lista_documentos.append(filename)
            print(f"Documento ya cargado: {filename}") 
            continue

        # Cargar el contenido del archivo
        data = loader.load()
        contador_doc += 1
        print(f"N° documentos cargados: {contador_doc}")
        lista_documentos.append(filename)
        
        # Dividir el contenido del documento en fragmentos
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n"],
            chunk_size=512,
            chunk_overlap=128,
            add_start_index=True
        )

        # Procesar cada documento cargado
        for doc in data:
            doc.metadata = {"document": filename}  # Agregar metadatos
            print("Metadatos del documento:", doc.metadata)
            splits = text_splitter.split_documents([doc])  # Dividir en fragmentos
            vector_store.add_documents(splits)  # Agregar fragmentos a la base de vectores
        
    return lista_documentos
