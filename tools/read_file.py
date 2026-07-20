from pathlib import Path
from langchain_core.tools import tool
from .file_utils import find_file

REPO_PATH = Path("repositories/langgraph")


@tool
def read_file(file_name: str) -> str:
    """
    Read and return the COMPLETE contents of a file.

    Use this tool whenever the user asks:
    - show app.py
    - display app.py
    - what does app.py contain
    - give me app.py
    - print app.py
    - read app.py
    - give me requirements.txt
    - show requirements.txt

    Return the exact file contents with no summary and no added commentary.
    """
    file_name = file_name.replace("\\", "/")

    # Handle full relative paths
    path = REPO_PATH / Path(file_name)
    if path.exists():
        return path.read_text(encoding="utf-8")
    
    matches = find_file(file_name)

    if not matches:
        return f"No file named '{file_name}' was found."

    if len(matches) > 1:
        return (
            f"Multiple files named '{file_name}' were found:\n"
            + "\n".join(matches)
            + "\nPlease specify the path."
        )

    file_path = Path(matches[0])

    try:
        content = file_path.read_text(encoding="utf-8")
        return content

    except UnicodeDecodeError:
        return "Cannot display binary files."

    except Exception as e:
        return f"Error reading file: {e}"