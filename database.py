from langchain_community.vectorstores import FAISS
from embeddings import create_embeddings

def create_database(chunks):
    embeddings = create_embeddings()

    vectorstore = FAISS.from_documents(
       chunks, 
       embeddings
    )

    vectorstore.save_local("vectorstore")

