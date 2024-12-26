"""
Módulo de carga de documentos en ChromaDB con LangChain.

Este módulo permite cargar un documento `.docx`, dividirlo en fragmentos adecuados, 
generar embeddings utilizando Cohere, y almacenarlos en una base de datos vectorial (ChromaDB).

Funcionalidades principales:
- Carga de un documento de texto en formato `.docx`.
- División del texto en fragmentos (chunks) utilizando un divisor recursivo.
- Creación de embeddings mediante el modelo de Cohere.
- Persistencia de los embeddings en ChromaDB.
"""
import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

def cargar_documentos_en_chroma_db(directory):
    """
    Carga un documento en ChromaDB, dividiéndolo en fragmentos, creando embeddings y almacenandolo en la base de vectores.

    Raises:
        FileNotFoundError: Si el archivo del documento no existe.
    """
    # Cargar documentos
    lista_documentos = []
    contador_doc = 0
    
    # Recorrer archivos en el directorio
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Verificar si es un archivo PDF o Word
        if filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            contador_doc += 1
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            contador_doc += 1
        else:
            print(f"Archivo ignorado (formato no soportado): {filename}")
            continue
        
        # Cargar el archivo
        data = loader.load()
        print("N° documentos cargados:", contador_doc)
        print(data)
        lista_documentos.extend(data)

    # Dividir el contenido en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=512,
        chunk_overlap=128,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(data)

    # Creacion de base de datos de vectores 
    vector_store = Chroma.from_documents(
        collection_name   = "documentos",
        documents         = all_splits, 
        embedding         = CohereEmbeddings(model="embed-multilingual-v2.0"), 
        persist_directory = './chroma_langchain_db'
    )
    
    #print(vector_store.similarity_search(query = "Quien es Zara?", k=3)) # Solo para test
    print("N° vectores en vector_store:", vector_store._collection.count(), "\n\n")
    print("Documentos cargados con éxito en ChromaDB.")

