from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader

from app.features.rag.parser import (
    enrich_metadata,
    parse_legal_sections,
)

from app.features.rag.chunker import chunk_documents

from app.features.rag.embeddings import (
    create_vectorstore,
    load_vectorstore,
)

from app.features.rag.retriever import retrieve

from app.features.rag.generator import (
    create_llm,
    generate_answer,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

VECTOR_DB_DIR = (
    BASE_DIR
    / "vector_db"
    / "legal_chroma_db"
)

COLLECTION_NAME = "legal_documents"


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/rag",
    tags=["Legal RAG"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================


class RAGQuery(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        description="Legal question",
    )

    k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve",
    )

    act: str | None = Field(
        default=None,
        description="Optional Act filter, e.g. ipc_1860",
    )


class SourceDocument(BaseModel):
    content: str

    act: str | None = None

    section: str | None = None

    chapter: str | None = None

    category: str | None = None

    source_file: str | None = None

    page: int | None = None

    chunk_id: int | None = None


class RAGResponse(BaseModel):
    query: str

    answer: str

    sources: list[SourceDocument]


# ============================================================
# GLOBAL STATE
# ============================================================

_vectorstore = None

_llm = None


# ============================================================
# VECTOR STORE
# ============================================================


def get_vectorstore():
    """
    Load the existing Chroma database lazily.
    """

    global _vectorstore

    if _vectorstore is None:

        if not VECTOR_DB_DIR.exists():

            raise RuntimeError(
                "Vector database does not exist. "
                "Run the ingestion endpoint first."
            )

        _vectorstore = load_vectorstore(
            persist_directory=VECTOR_DB_DIR,
            collection_name=COLLECTION_NAME,
        )

    return _vectorstore


# ============================================================
# LOCAL LLM
# ============================================================


def get_llm():
    """
    Create the local Ollama LLM lazily.
    """

    global _llm

    if _llm is None:

        _llm = create_llm(
            model="llama3.2",
            temperature=0,
        )

    return _llm


# ============================================================
# HEALTH
# ============================================================


@router.get("/health")
def rag_health():

    return {
        "status": "ok",
        "vector_database": VECTOR_DB_DIR.exists(),
        "data_directory": DATA_DIR.exists(),
    }


# ============================================================
# INGEST DOCUMENTS
# ============================================================


@router.post("/ingest")
def ingest_documents():

    global _vectorstore

    try:

        # ----------------------------------------------------
        # Check data directory
        # ----------------------------------------------------

        if not DATA_DIR.exists():

            raise HTTPException(
                status_code=404,
                detail=f"Data directory not found: {DATA_DIR}",
            )

        # ----------------------------------------------------
        # Find PDFs
        # ----------------------------------------------------

        pdf_files = list(
            DATA_DIR.rglob("*.pdf")
        )

        if not pdf_files:

            raise HTTPException(
                status_code=404,
                detail="No PDF documents found.",
            )

        documents = []

        total_pages = 0

        total_sections = 0

        # ----------------------------------------------------
        # Load and parse every PDF
        # ----------------------------------------------------

        for pdf_path in pdf_files:

            category = pdf_path.parent.name

            act_name = pdf_path.stem

            print(
                f"\nProcessing: {pdf_path.name}"
            )

            print(
                f"Category: {category}"
            )

            print(
                f"Act: {act_name}"
            )

            # ------------------------------------------------
            # Load PDF
            # ------------------------------------------------

            loader = PyPDFLoader(
                str(pdf_path)
            )

            pages = loader.load()

            total_pages += len(pages)

            print(
                f"Pages loaded: {len(pages)}"
            )

            # ------------------------------------------------
            # Add common metadata
            # ------------------------------------------------

            pages = enrich_metadata(
                documents=pages,
                category=category,
                act_name=act_name,
                source_file=pdf_path.name,
            )

            # ------------------------------------------------
            # Parse actual legal sections
            # ------------------------------------------------

            sections = parse_legal_sections(
                pages
            )

            total_sections += len(sections)

            print(
                f"Legal sections/pages produced: "
                f"{len(sections)}"
            )

            # ------------------------------------------------
            # Add parsed documents
            # ------------------------------------------------

            documents.extend(
                sections
            )

        # ----------------------------------------------------
        # Safety check
        # ----------------------------------------------------

        if not documents:

            raise HTTPException(
                status_code=500,
                detail=(
                    "No documents were produced "
                    "after parsing."
                ),
            )

        # ----------------------------------------------------
        # Chunk legal sections
        # ----------------------------------------------------
        #
        # Legal-aware chunks should be reasonably large so
        # that subsection context is not unnecessarily lost.
        #
        # ----------------------------------------------------

        chunks = chunk_documents(
            documents,
            chunk_size=1600,
            chunk_overlap=150,
        )

        print(
            f"\nTotal parsed documents: "
            f"{len(documents)}"
        )

        print(
            f"Total chunks: "
            f"{len(chunks)}"
        )

        # ----------------------------------------------------
        # Create Chroma vector database
        # ----------------------------------------------------

        _vectorstore = create_vectorstore(
            documents=chunks,
            persist_directory=VECTOR_DB_DIR,
            collection_name=COLLECTION_NAME,
        )

        return {
            "status": "success",
            "pdf_files": len(pdf_files),
            "pages": total_pages,
            "parsed_documents": total_sections,
            "chunks": len(chunks),
            "vector_database": str(
                VECTOR_DB_DIR
            ),
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(exc)}",
        )


# ============================================================
# QUERY
# ============================================================


@router.post(
    "/query",
    response_model=RAGResponse,
)
def query_legal_rag(
    request: RAGQuery,
):

    try:

        # ----------------------------------------------------
        # Load resources
        # ----------------------------------------------------

        vectorstore = get_vectorstore()

        llm = get_llm()

        # ----------------------------------------------------
        # Optional Act filter
        # ----------------------------------------------------

        metadata_filter = None

        if request.act:

            metadata_filter = {
                "act": request.act
            }

        # ----------------------------------------------------
        # Retrieve documents
        # ----------------------------------------------------

        documents = retrieve(
            vectorstore=vectorstore,
            query=request.query,
            k=request.k,
            filter=metadata_filter,
        )

        # ----------------------------------------------------
        # No results
        # ----------------------------------------------------

        if not documents:

            return RAGResponse(
                query=request.query,
                answer=(
                    "## Answer\n\n"
                    "I could not find relevant information "
                    "in the provided legal documents."
                ),
                sources=[],
            )

        # ----------------------------------------------------
        # Generate Markdown answer
        # ----------------------------------------------------

        answer = generate_answer(
            query=request.query,
            documents=documents,
            llm=llm,
        )

        # ----------------------------------------------------
        # Build sources
        # ----------------------------------------------------

        sources = []

        for doc in documents:

            metadata = doc.metadata or {}

            page_value = metadata.get(
                "page",
                metadata.get("start_page"),
            )

            # Make sure page is an integer when possible.
            if page_value is not None:

                try:
                    page_value = int(page_value)

                except (
                    TypeError,
                    ValueError,
                ):

                    page_value = None

            chunk_id_value = metadata.get(
                "chunk_id"
            )

            if chunk_id_value is not None:

                try:
                    chunk_id_value = int(
                        chunk_id_value
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    chunk_id_value = None

            sources.append(
                SourceDocument(
                    content=doc.page_content,

                    act=metadata.get(
                        "act"
                    ),

                    section=metadata.get(
                        "section"
                    ),

                    chapter=metadata.get(
                        "chapter"
                    ),

                    category=metadata.get(
                        "category"
                    ),

                    source_file=metadata.get(
                        "source_file"
                    ),

                    page=page_value,

                    chunk_id=chunk_id_value,
                )
            )

        # ----------------------------------------------------
        # Final API response
        # ----------------------------------------------------

        return RAGResponse(
            query=request.query,
            answer=answer,
            sources=sources,
        )

    except HTTPException:

        raise

    except Exception as exc:

        print(
            "\n"
            "=================================================="
        )

        print(
            "RAG QUERY ERROR"
        )

        print(
            "=================================================="
        )

        print(
            f"Error type: {type(exc).__name__}"
        )

        print(
            f"Error: {exc}"
        )

        print(
            "=================================================="
        )

        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(exc)}",
        )


# ============================================================
# DEBUG: SEMANTIC SEARCH
# ============================================================


@router.get("/debug/search")
def debug_search(
    query: str,
    k: int = 5,
):

    try:

        vectorstore = get_vectorstore()

        documents = vectorstore.similarity_search(
            query,
            k=k,
        )

        return {
            "query": query,
            "count": len(documents),

            "results": [
                {
                    "content": doc.page_content,

                    "metadata": doc.metadata,
                }

                for doc in documents
            ],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# DEBUG: EXACT SECTION SEARCH
# ============================================================


@router.get(
    "/debug/section/{section_number}"
)
def debug_section(
    section_number: str,
):

    try:

        vectorstore = get_vectorstore()

        # ----------------------------------------------------
        # Search Chroma using exact metadata
        # ----------------------------------------------------

        results = vectorstore.get(
            where={
                "section": section_number
            }
        )

        documents = results.get(
            "documents",
            [],
        )

        metadatas = results.get(
            "metadatas",
            [],
        )

        # ----------------------------------------------------
        # Build response
        # ----------------------------------------------------

        output = []

        for index, content in enumerate(
            documents
        ):

            metadata = {}

            if index < len(metadatas):

                metadata = (
                    metadatas[index]
                    or {}
                )

            output.append(
                {
                    "content": content,
                    "metadata": metadata,
                }
            )

        return {
            "section": section_number,
            "count": len(output),
            "results": output,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Section debug failed: {str(exc)}"
            ),
        )