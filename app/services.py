"""
Módulo de procesamiento de consultas mediante recuperación de contexto y generación de respuestas.

Este módulo realiza las siguientes operaciones:
1. Recupera documentos relacionados con la consulta del usuario desde un vector store utilizando Chroma.
2. Detecta el idioma de la consulta mediante un modelo de lenguaje.
3. Genera una respuesta basada en los fragmentos de contexto recuperados.
4. Traduce la respuesta generada al idioma detectado o especificado.

Dependencias:
- langchain_chroma (Chroma): Para búsqueda de similitud en documentos.
- langchain_cohere (ChatCohere): Para generación de texto y tareas de procesamiento del lenguaje.
- app.models (SolicitudConsulta): Modelo Pydantic que define la estructura de la consulta.

Funciones principales:
- retrieve(): Recupera documentos relevantes basados en la consulta.
- detectar_idioma(): Detecta el idioma de la consulta del usuario.
- generar_respuesta(): Genera una respuesta utilizando el contexto recuperado.
- traducir_respuesta(): Traduce la respuesta generada al idioma especificado.
- procesar_consulta(): Orquesta todo el flujo: recuperación, generación y traducción.
"""

from langchain_chroma import Chroma
from app.models import SolicitudConsulta
from langchain_cohere import ChatCohere
from langchain_cohere import CohereEmbeddings

# Inicialización del modelo Cohere
llm = ChatCohere(model="command-r-plus-04-2024", temperature=0)

# Cargando documento de la Base de Vectores
chroma_local = Chroma(
    collection_name="documentos",
    embedding_function=CohereEmbeddings(model="embed-multilingual-v2.0"),
    persist_directory="./chroma_langchain_db"
)

def preprocess_docs(docs):
    seen = set()
    unique_docs = []
    for doc in docs:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)
    return unique_docs

def retrieve(state: SolicitudConsulta):
    """
    Recupera documentos relacionados con la consulta del usuario desde el vector store.

    Parameters:
        state (SolicitudConsulta): Contiene la pregunta y el nombre del usuario.

    Returns:
        dict: Contexto con los fragmentos de documentos relevantes.
    """
    retrieved_docs = chroma_local.similarity_search(query = state.question, k=3)
    filtered_docs = preprocess_docs(retrieved_docs)
    print(filtered_docs)
    return {"context": [doc.page_content for doc in retrieved_docs]}

def detectar_idioma(state: SolicitudConsulta):
    """
    Detecta el idioma de la consulta utilizando un modelo de lenguaje.

    Parameters:
        state (SolicitudConsulta): Contiene la pregunta del usuario.

    Returns:
        str: Código del idioma detectado (por ejemplo, 'es' para español).
    """
    # Incluir ejemplos para el modelo de detección de idioma
    few_shot_examples = """
    Ejemplo 1:
    Pregunta: ¿Cómo estás?
    Respuesta: es

    Ejemplo 2:
    Question: How are you?
    Answer: en

    Exemplo 3:
    Pergunta: Como você está?
    Resposta: pt
    """

    prompt = f"""
    {few_shot_examples}
    Eres un asistente especializado en detectar idiomas. 
    Genera la respuesta en el formato mencionado en los ejemplos. 
    Si no puedes determinarlo con certeza, responde 'es' por defecto.

    Pregunta: {state.question}
     
    Respuesta:
    """
    response = llm.invoke(prompt)
    print(f'Idioma detectado: {response.content}')
    return response.content

def generar_respuesta(state: SolicitudConsulta, context: list):
    """
    Genera una respuesta utilizando el contexto recuperado de los documentos.

    Parameters:
        state (SolicitudConsulta): Contiene la pregunta del usuario.
        context (list): Lista de fragmentos de documentos relacionados.

    Returns:
        str: Respuesta generada.
    """
    prompt = """
    Eres un asistente de preguntas y respuestas diseñado para proporcionar respuestas precisas y breves.
    Usa los fragmentos de contexto recuperados para generar la respuesta. 
    Si no conoces la respuesta, indica claramente que no la sabes. 
    Mantén las respuestas en un máximo de una oración y sé conciso.
    Detecta el idioma en el que se formula la pregunta y responde en el mismo idioma.
    Añade un emoji al final que resuma o complemente la respuesta.
    Responde siempre en tercera persona.

    Pregunta: {question}    

    Contexto: {context}

    Respuesta:
    """
    formatted_prompt = prompt.format(
        question=state.question, 
        context="\n\n".join(context)
    )
    #print(context)
    response = llm.invoke(formatted_prompt)
    return response.content

def traducir_respuesta(state: SolicitudConsulta, texto: str, idioma_destino: str):
    """
    Traduce la respuesta generada al idioma deseado.

    Parameters:
        state (SolicitudConsulta): Contiene el nombre del usuario.
        texto (str): El texto que se desea traducir.
        idioma_destino (str): El idioma de destino (código ISO 639-1, como 'es' para español).

    Returns:
        dict: Contiene el nombre del usuario y la respuesta traducida.
    """
    few_shot_examples = """
    Ejemplo 1:
    Texto: Emma decided to share her extra day with the people. 🌟🤸‍♀️
    Idioma destino: es
    Traducción: Emma decidió compartir su día extra con el pueblo. 🌟🤸‍♀️

    Ejemplo 2:
    Texto: Emma decidiu compartilhar seu dia extra com o povo. 🌟🤸‍♀️
    Idioma destino: en
    Traducción: Emma decided to share her extra day with the people. 🌟🤸‍♀️

    Ejemplo 3:
    Texto: Emma decidió compartir su día extra con el pueblo. 🌟🤸‍♀️
    Idioma destino: pt
    Traducción: Emma decidiu compartilhar seu dia extra com o povo. 🌟🤸‍♀️
    """

    prompt = f"""
    {few_shot_examples}
    Solo traduce el siguiente texto al idioma indicado manteniendo los emojis al final.

    Texto: {texto}
    Idioma destino: {idioma_destino}

    Traducción:
    """
    try:
        response = llm.invoke(prompt)
        return response.content
    
    except Exception as e:
        print(f"Error al traducir con el modelo: {e}")
        return texto  # Devuelve el texto original si hay un fallo

def procesar_consulta(state: SolicitudConsulta):
    """
    Procesa una consulta desde el usuario: recuperar contexto, generar y traducir la respuesta.

    Parameters:
        state (SolicitudConsulta): Contiene la consulta del usuario.

    Returns:
        dict: Contiene la respuesta generada, ya traducida si es necesario.
    """
    context_data = retrieve(state)
    print(context_data)
    idioma_detectado = detectar_idioma(state)
    respuesta_base = generar_respuesta(state, context_data["context"])
    
    if idioma_detectado == "es":
        respuesta_final = respuesta_base
    else:
        respuesta_final = traducir_respuesta(state, respuesta_base, idioma_detectado)

    respuesta_final = {
        "user_name": state.user_name,
        "answer": respuesta_final,
    }
    
    return respuesta_final
