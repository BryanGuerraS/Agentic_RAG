from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

chroma_local = Chroma(
    collection_name="documentos", 
    embedding_function=CohereEmbeddings(model="embed-multilingual-v2.0"), 
    persist_directory="chroma_db/preprocessed" 
) 
print("holi")
print(chroma_local)
print("holi")