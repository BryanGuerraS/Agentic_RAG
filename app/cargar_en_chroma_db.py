import os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

def cargar_documentos_en_chroma_db(directory, persist_directory, flag_nuevo):
    """
    Carga documentos en ChromaDB, los divide en fragmentos, crea embeddings y los almacena en la base de vectores.

    Raises:
        FileNotFoundError: Si el archivo del documento no existe.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"El directorio '{directory}' no existe.")
    
    # Cargar documentos
    lista_documentos = []
    documentos_ya_cargados = set()
    contador_doc = 0

    vector_store = Chroma(
        collection_name="documentos", 
        embedding_function=CohereEmbeddings(model="embed-multilingual-v2.0"), 
        persist_directory=persist_directory
    )
        
    for doc in vector_store.get()['metadatas']: 
        documentos_ya_cargados.add(doc['document'])
    print(documentos_ya_cargados)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Verificar si es un archivo PDF o Word
        if filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        
        # Verificar si el documento ya ha sido cargado 
        if filename in documentos_ya_cargados: 
            if flag_nuevo == False:
                lista_documentos.append(filename)
            print(f"Documento ya cargado: {filename}") 
            continue

        # Cargar el archivo
        data = loader.load()
        contador_doc += 1
        print(f"N° documentos cargados: {contador_doc}")
        lista_documentos.append(filename)
        
        # Añadir metadatos al documento y dividir en fragmentos
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n"],
            chunk_size=512,
            chunk_overlap=128,
            add_start_index=True
        )

        for doc in data:
            doc.metadata = {"document": filename}
            print(doc.metadata)
            splits = text_splitter.split_documents([doc])
            vector_store.add_documents(splits)
        
    return lista_documentos
