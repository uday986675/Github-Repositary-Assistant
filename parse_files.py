import os
from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    NotebookLoader,
)

repo_path = Path("repositories/langgraph")
IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".exe",
    ".dll",
    ".so",
    ".pyc",
    ".keras",
    ".h5",
    ".pkl",
    ".pickle",
    ".bin",
    ".dat",
    ".npy",
    ".npz",
    ".pt",
    ".pth",
    ".onnx",
    ".pb",
    ".hdf5"
}
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build"
}
LOADERS = {
    ".pdf": PyPDFLoader,
    ".csv": CSVLoader,
    ".ipynb": NotebookLoader,
}

documents = []
def file_parser():
    for root, dirs, files in os.walk("repositories/langgraph"):
        # Prevent os.walk from entering ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            suffix = file_path.suffix.lower()
            loader_cls = LOADERS.get(suffix, TextLoader)
            
            try:
                # Use UTF-8 encoding for TextLoader to avoid UnicodeDecodeError on Windows
                if loader_cls == TextLoader:
                    loader = loader_cls(str(file_path), encoding="utf-8")
                else:
                    loader = loader_cls(str(file_path))
                
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    return documents

# print(documents)
