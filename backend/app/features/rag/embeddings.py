from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_COLLECTION = "legal_documents"


# ============================================================
# EMBEDDINGS
# ============================================================

def create_embeddings(
    model: str = DEFAULT_MODEL,
) -> HuggingFaceEmbeddings:
    """
    Create a local Hugging Face embedding model.

    No OpenAI API key is required.
    """
    return HuggingFaceEmbeddings(
        model_name=model,
    )


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vectorstore(
    documents: list[Document],
    persist_directory: str | Path,
    model: str = DEFAULT_MODEL,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """
    Create a Chroma vector database from documents.

    Embeddings are generated locally.
    """

    embeddings = create_embeddings(model)

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(persist_directory),
        collection_name=collection_name,
    )

    return vectorstore


# ============================================================
# LOAD VECTOR STORE
# ============================================================

def load_vectorstore(
    persist_directory: str | Path,
    model: str = DEFAULT_MODEL,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """
    Load an existing Chroma vector database.
    """

    embeddings = create_embeddings(model)

    vectorstore = Chroma(
        persist_directory=str(persist_directory),
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    return vectorstore