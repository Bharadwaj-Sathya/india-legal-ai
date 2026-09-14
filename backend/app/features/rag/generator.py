from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "llama3.2"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a legal information assistant for an Indian legal document
retrieval system.

============================================================
ABSOLUTE GROUNDING RULE
============================================================

Answer ONLY from the retrieved legal context.

Never use your pretrained/general legal knowledge.

Never infer missing legal information.

Never convert a legal duty, procedure, restriction, power,
condition, or exception into a "right" unless the retrieved text
explicitly establishes that right.

============================================================
LEGAL PROVISION CLASSIFICATION
============================================================

Before describing each section, determine what the retrieved text
actually establishes.

Possible classifications include:

- RIGHT / ENTITLEMENT
- DUTY / OBLIGATION
- PROCEDURE
- RESTRICTION / LIMITATION
- POWER / DISCRETION
- CONDITION
- EXCEPTION
- PROHIBITION
- PERMISSION

Preserve the classification in the answer.

For example:

If the provision says that a police officer "shall not detain"
a person beyond a specified period, describe it as a restriction
or limitation on detention.

DO NOT describe it as:

"You have a right to be detained for that period."

If a provision says that a person "shall be taken before"
a Magistrate, describe it as a statutory procedure or duty.

DO NOT automatically describe it as:

"You have a right to be taken before a Magistrate."

If a provision says that a Magistrate "shall" take an action
when specified conditions are satisfied, preserve those conditions.

If a provision contains "unless", "if", "subject to", "provided",
"except", or similar language, include the relevant condition or
exception.

============================================================
NO INFERENCE
============================================================

Do NOT use phrases such as:

- "it is implied"
- "this implies"
- "it can be inferred"
- "generally this means"
- "this means that the person has a right"
- "in practice"
- "under general law"
- "commonly understood"
- "as a general legal principle"

unless the retrieved text itself explicitly supports that
statement.

============================================================
SECTION 54 EXAMPLE
============================================================

If the retrieved text for Section 54 says that an arrested person
may request an examination when specified conditions are satisfied,
describe those conditions.

Do NOT summarize Section 54 simply as:

"The arrested person has an unconditional right to medical
examination."

============================================================
SECTION 57 EXAMPLE
============================================================

If the retrieved text says:

"No police officer shall detain..."

describe this as a limitation on police detention.

Do NOT say:

"The person has a right to be detained for 24 hours."

Also preserve the exception involving a special order under
Section 167 and the exclusion of journey time where stated in
the retrieved text.

============================================================
SECTION 56 EXAMPLE
============================================================

If the retrieved text states that a person arrested is to be
taken before a Magistrate or officer in charge, describe the
statutory procedure/duty.

Do NOT automatically call it a personal "right" unless the
retrieved text explicitly uses or establishes that entitlement.

============================================================
INCOMPLETE CONTEXT
============================================================

If the retrieved text is incomplete, do not reconstruct the
missing portion.

Do not use outside knowledge to complete it.

Clearly state that the retrieved context is incomplete when
necessary.

============================================================
MULTIPLE SECTIONS
============================================================

You may combine multiple retrieved provisions.

For every important legal claim:

1. Identify the section.
2. State what the provision actually establishes.
3. Preserve its conditions and exceptions.
4. Do not change the legal classification.

============================================================
ANSWER STYLE
============================================================

Keep the answer concise and factual.

Use this structure when appropriate:

Section XX — [what the provision establishes]

Explain only what is explicitly supported by the retrieved text.

If the retrieved context does not contain enough information
to answer the question, say so.

Answer ONLY from the supplied legal context.
"""
# ============================================================
# LOCAL OLLAMA LLM
# ============================================================

def create_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = 0,
) -> ChatOllama:
    """
    Create the local Ollama language model.

    Default model:
        llama3.2

    This does NOT require an OpenAI API key.
    """

    return ChatOllama(
        model=model,
        temperature=temperature,
    )


# ============================================================
# PROMPT
# ============================================================

def create_prompt() -> ChatPromptTemplate:
    """
    Create the prompt used by the legal RAG generator.
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            (
                "human",
                """
Legal context retrieved from the document database:

{context}

--------------------------------------------------

User question:

{question}

--------------------------------------------------

Instructions:

Answer the user's question using only the legal context above.

If the context does not contain sufficient information, say so
clearly instead of using outside knowledge.

Answer:
""",
            ),
        ]
    )


# ============================================================
# DOCUMENT FORMATTING
# ============================================================

def format_documents(
    documents: list[Document],
) -> str:
    """
    Convert retrieved LangChain documents into a structured
    context string for the LLM.
    """

    if not documents:
        return "No legal documents were retrieved."

    formatted: list[str] = []

    for index, document in enumerate(documents, start=1):

        metadata = document.metadata or {}

        act = metadata.get("act", "unknown")
        section = metadata.get("section", "unknown")
        chapter = metadata.get("chapter", "unknown")
        category = metadata.get("category", "unknown")
        page = metadata.get("page", "unknown")
        source_file = metadata.get("source_file", "unknown")
        chunk_id = metadata.get("chunk_id", "unknown")

        source = (
            f"Source {index}\n"
            f"Act: {act}\n"
            f"Section: {section}\n"
            f"Chapter: {chapter}\n"
            f"Category: {category}\n"
            f"Page: {page}\n"
            f"Source file: {source_file}\n"
            f"Chunk ID: {chunk_id}\n"
        )

        content = document.page_content.strip()

        formatted.append(
            f"{source}\n"
            f"Text:\n"
            f"{content}"
        )

    return "\n\n==============================\n\n".join(formatted)


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    query: str,
    documents: list[Document],
    llm: ChatOllama | None = None,
) -> dict[str, Any]:
    """
    Generate a legal answer from retrieved documents.

    Parameters
    ----------
    query:
        User's legal question.

    documents:
        Documents retrieved from Chroma.

    llm:
        Optional Ollama LLM instance.

    Returns
    -------
    dict
        {
            "answer": "...",
            "documents": [...]
        }
    """

    # --------------------------------------------------------
    # Create LLM if one was not provided
    # --------------------------------------------------------

    if llm is None:
        llm = create_llm(
            model=DEFAULT_MODEL,
            temperature=0,
        )

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = create_prompt()

    # --------------------------------------------------------
    # Format retrieved documents
    # --------------------------------------------------------

    context = format_documents(documents)

    # --------------------------------------------------------
    # Build messages
    # --------------------------------------------------------

    messages = prompt.invoke(
        {
            "context": context,
            "question": query,
        }
    )

    # --------------------------------------------------------
    # Generate answer using Ollama
    # --------------------------------------------------------

    response = llm.invoke(messages)

    # --------------------------------------------------------
    # Return answer + sources
    # --------------------------------------------------------

    return {
        "answer": response.content,
        "documents": documents,
    }