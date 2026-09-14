from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader

from rag.parser import enrich_metadata
from rag.chunker import chunk_documents
from rag.embeddings import create_vectorstore, load_vectorstore
from rag.retriever import retrieve
from rag.generator import create_llm, generate_answer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db" / "legal_chroma_db"

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
        description="Legal question"
    )

    k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve"
    )

    act: str | None = Field(
        default=None,
        description="Optional Act filter, e.g. ipc_1860"
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
# VECTOR STORE
# ============================================================

_vectorstore = None
_llm = None


def get_vectorstore():
    """
    Load the existing Chroma database.

    This is loaded lazily so the application can start
    without immediately initializing the embedding model.
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


def get_llm():

    global _llm

    if _llm is None:
        _llm = create_llm(
            model="gpt-5.6",
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

    try:

        if not DATA_DIR.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Data directory not found: {DATA_DIR}",
            )

        pdf_files = list(DATA_DIR.rglob("*.pdf"))

        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail="No PDF documents found.",
            )

        documents = []

        # ----------------------------------------------------
        # Load PDFs
        # ----------------------------------------------------

        for pdf_path in pdf_files:

            category = pdf_path.parent.name
            act_name = pdf_path.stem

            loader = PyPDFLoader(str(pdf_path))

            pages = loader.load()

            # ------------------------------------------------
            # Legal metadata
            # ------------------------------------------------

            pages = enrich_metadata(
                documents=pages,
                category=category,
                act_name=act_name,
                source_file=pdf_path.name,
            )

            documents.extend(pages)

        # ----------------------------------------------------
        # Chunk
        # ----------------------------------------------------

        chunks = chunk_documents(
            documents,
            chunk_size=700,
            chunk_overlap=100,
        )

        # ----------------------------------------------------
        # Create vector database
        # ----------------------------------------------------

        global _vectorstore

        _vectorstore = create_vectorstore(
            documents=chunks,
            persist_directory=VECTOR_DB_DIR,
            collection_name=COLLECTION_NAME,
        )

        return {
            "status": "success",
            "pdf_files": len(pdf_files),
            "pages": len(documents),
            "chunks": len(chunks),
            "vector_database": str(VECTOR_DB_DIR),
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
def query_legal_rag(request: RAGQuery):

    try:

        vectorstore = get_vectorstore()
        llm = get_llm()

        # ----------------------------------------------------
        # Metadata filter
        # ----------------------------------------------------

        metadata_filter = None

        if request.act:
            metadata_filter = {
                "act": request.act
            }

        # ----------------------------------------------------
        # Retrieval
        # ----------------------------------------------------

        documents = retrieve(
            vectorstore=vectorstore,
            query=request.query,
            k=request.k,
            filter=metadata_filter,
        )

        if not documents:

            return RAGResponse(
                query=request.query,
                answer=(
                    "I could not find relevant information "
                    "in the provided legal documents."
                ),
                sources=[],
            )

        # ----------------------------------------------------
        # Generation
        # ----------------------------------------------------

        result = generate_answer(
            query=request.query,
            documents=documents,
            llm=llm,
        )

        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        sources = []

        for doc in result["documents"]:

            metadata = doc.metadata

            sources.append(
                SourceDocument(
                    content=doc.page_content,
                    act=metadata.get("act"),
                    section=metadata.get("section"),
                    chapter=metadata.get("chapter"),
                    category=metadata.get("category"),
                    source_file=metadata.get("source_file"),
                    page=metadata.get("page"),
                    chunk_id=metadata.get("chunk_id"),
                )
            )

        return RAGResponse(
            query=request.query,
            answer=result["answer"],
            sources=sources,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(exc)}",
        )