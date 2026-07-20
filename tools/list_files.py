from pathlib import Path
from langchain_core.tools import tool

REPO_PATH = Path("repositories/langgraph")

@tool
def list_files(extension : str) -> list:
    """
    List all files in the repository matching a given file extension.

    Use this tool when the user wants to discover multiple files rather than a
    specific file.

    Examples:
    - List all .txt files
    - Show every Python file
    - Find all .py files
    - List all Markdown files
    - Show every JSON file
    - Find all YAML files
    - List all test files with the .py extension

    Do NOT use this tool when the user asks for:
    - the contents of a file (use read_file)
    - the location of a specific file (use find_file_tool)
    - an explanation or summary of the repository (use answer_repository_question)

    Args:
        extension: The file extension to search for (e.g. "py", "txt", "md", "json", "yaml").

    Returns:
        A list of matching file paths.
    """
    matches = []
    extension = extension.lstrip('.')

    for file in REPO_PATH.rglob('*'):
        if file.is_file() and file.suffix == f".{extension}":
            matches.append(str(file))

    return matches
