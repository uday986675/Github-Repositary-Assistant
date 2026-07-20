from langchain_core.tools import tool
from .file_utils import retrieve, generate

@tool
def answer_repository_question(question : str) -> str:
    """
    Answer high-level questions about the repository.

    Use this tool only when the user asks:
    - how the project works
    - explain the architecture
    - summarize functionality
    - explain algorithms
    - describe implementation

    Do NOT use this tool when the user asks:
    - show a file
    - display code
    - print the contents of a file
    - read app.py
    """
    context = retrieve(question)
    return generate(question, context=context)