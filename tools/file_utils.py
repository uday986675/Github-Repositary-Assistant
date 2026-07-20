from pathlib import Path
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from retriever import get_retriever
from dotenv import load_dotenv
from prompts import QA_PROMPT

REPO_PATH = Path("repositories/langgraph")
load_dotenv()
def get_model():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

def find_file(file_name):
    matches = []

    for file in REPO_PATH.rglob("*"):
        if file.is_file() and file.name == file_name:
            matches.append(str(file))

    return matches

def retrieve(question):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    context = '\n\n'.join(doc.page_content for doc in docs)
    return context

def generate(question, context):
    prompt = QA_PROMPT
    model = get_model()
    chain = prompt | model | StrOutputParser()
    answer = chain.invoke({
        "context": context,
        "question": question
    })
    return answer
