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
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

def cargar_documento_en_chroma_db():
    """
    Carga un documento en ChromaDB, dividiéndolo en fragmentos, creando embeddings y almacenandolo en la base de vectores.

    Raises:
        FileNotFoundError: Si el archivo del documento no existe.
    """
    # Cargar el documento
    try:
        loader = Docx2txtLoader("Documentos de ejemplo/documento.docx")
        data = loader.load()
    except FileNotFoundError:
        raise FileNotFoundError("El archivo 'documento.docx' no fue encontrado.")

    # Dividir el contenido en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=512,
        chunk_overlap=128,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(data)

    # Creacion de base de datos de vectores 
    Chroma.from_documents(
        collection_name   = "documentos",
        documents         = all_splits, 
        embedding         = CohereEmbeddings(model="embed-multilingual-v2.0"), 
        persist_directory = './chroma_langchain_db'
    )
    
    #print(vector_store.similarity_search(query = "Quien es Zara?", k=3)) # Solo para test

    print("Documento cargado con éxito en ChromaDB.")

