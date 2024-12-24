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

vector_store = None

def cargar_documento_en_chroma_db():
    """
    Carga un documento en ChromaDB, dividiéndolo en fragmentos y creando embeddings.

    Raises:
        FileNotFoundError: Si el archivo del documento no existe.
    """
    global vector_store

    # Cargar el documento
    try:
        loader = Docx2txtLoader("archivos/documento.docx")
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

    # Crear embeddings
    embeddings = CohereEmbeddings(model="embed-english-v3.0")

    # Cargar y persistir en Chroma
    vector_store = Chroma(
        collection_name="example_02",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db"
    )

    vector_store.add_documents(documents=all_splits)
    
    print("Documento cargado con éxito en ChromaDB.")

    return vector_store

