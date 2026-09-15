from __future__ import annotations

from typing import Iterable, Iterator

from langchain_core.documents import Document
from langchain_ollama import ChatOllama


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "llama3.2"
DEFAULT_TEMPERATURE = 0.0


# ============================================================
# CREATE LLM
# ============================================================

def create_llm(
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
) -> ChatOllama:

    return ChatOllama(
        model=model,
        temperature=temperature,
    )


# ============================================================
# FORMAT SOURCES
# ============================================================

def format_sources(
    documents: Iterable[Document],
) -> str:

    formatted = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        metadata = document.metadata or {}

        act = metadata.get(
            "act",
            "Unknown Act",
        )

        section = metadata.get(
            "section",
            "Unknown Section",
        )

        title = metadata.get(
            "section_title",
            "",
        )

        chapter = metadata.get(
            "chapter",
            "",
        )

        page = metadata.get(
            "page",
            metadata.get(
                "start_page",
                "Unknown",
            ),
        )

        content = document.page_content.strip()

        formatted.append(
            f"""
============================================================
SOURCE {index}
============================================================

**Act:** {act}

**Section:** {section}

**Title:** {title}

**Chapter:** {chapter}

**Page:** {page}

### Legal Text

{content}

============================================================
END SOURCE {index}
============================================================
""".strip()
        )

    return "\n\n".join(formatted)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an Indian Legal AI assistant.

Your task is to answer the user's question using ONLY the
retrieved legal sources provided below.

Your response MUST be valid Markdown.

============================================================
STRICT SOURCE ISOLATION
============================================================

Each SOURCE is an independent legal document.

1. Every legal claim must be supported by the exact source
   containing that claim.

2. Never mix information from different sections.

3. Never attribute information from Section 54 to Section 46,
   or from one Act to another Act.

4. The Act and Section mentioned for a claim must belong to
   the same source containing the supporting text.

5. Do not use outside legal knowledge.

6. Do not invent missing information.

7. Do not infer a legal right when the source only describes:
   - a police duty
   - a procedure
   - a restriction
   - a power
   - an obligation

8. Preserve conditions and exceptions from the source.

9. Do not remove qualifying words such as:
   - shall
   - may
   - unless
   - where
   - if
   - without warrant
   - subject to
   - non-bailable offence

10. If the retrieved sources do not establish something,
    say that the retrieved text does not establish it.

============================================================
LEGAL ACCURACY
============================================================

Be especially careful with:

- arrest
- detention
- bail
- grounds of arrest
- medical examination
- production before Magistrate
- warrant and warrantless arrest
- bailable and non-bailable offences
- police powers
- statutory duties
- statutory rights

Do not call something an unconditional "right" unless the
provided legal text supports that characterization.

============================================================
MARKDOWN FORMAT
============================================================

Use Markdown.

Prefer:


### Relevant Provisions

- **Section X — Act**
  - Explanation.

### What This Means

Practical explanation.

### Important Conditions

Conditions and exceptions.

### Sources

Relevant sections.

Use:

- headings
- bold text
- bullet points
- numbered lists
- blockquotes where useful

Do NOT return JSON.

Do NOT return HTML.

Do NOT put the entire answer inside a code block.

============================================================
NO HALLUCINATION
============================================================

Never invent:

- section numbers
- legal rights
- procedures
- punishments
- exceptions
- case law
- court decisions
- constitutional provisions

If the retrieved information is insufficient, say:

"The retrieved legal text does not provide enough information
to answer this part."

============================================================
DISCLAIMER
============================================================

End the response with:

> **Note:** This answer is based only on the retrieved statutory
> text and is for legal information purposes, not a substitute
> for advice from a qualified lawyer.
"""


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(
    query: str,
    documents: list[Document],
) -> str:

    context = format_sources(documents)

    return f"""
{SYSTEM_PROMPT}

============================================================
USER QUESTION
============================================================

{query}

============================================================
RETRIEVED LEGAL SOURCES
============================================================

{context}

============================================================
FINAL INSTRUCTIONS
============================================================

Answer the user's question now.

Return ONLY the final Markdown answer.

Before making every legal claim, verify:

1. Which SOURCE contains the claim?
2. Which Act does that SOURCE belong to?
3. Which Section does that SOURCE belong to?
4. Does the source actually support the claim?
5. Are there conditions or exceptions?
6. Am I accidentally using information from another section?

Do not mix sources.

Return Markdown, not JSON.
"""


# ============================================================
# NORMAL GENERATION
# ============================================================

def generate_answer(
    query: str,
    documents: list[Document],
    llm: ChatOllama,
) -> str:

    if not documents:

        return (
            "## Answer\n\n"
            "I could not find relevant information "
            "in the provided legal documents."
        )

    prompt = build_prompt(
        query=query,
        documents=documents,
    )

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        return str(
            response.content
        ).strip()

    return str(response).strip()


# ============================================================
# STREAMING GENERATION
# ============================================================

def stream_answer(
    query: str,
    documents: list[Document],
    llm: ChatOllama,
) -> Iterator[str]:

    if not documents:

        yield (
            "## Answer\n\n"
            "I could not find relevant information "
            "in the provided legal documents."
        )

        return

    prompt = build_prompt(
        query=query,
        documents=documents,
    )

    # --------------------------------------------------------
    # Ollama streaming
    # --------------------------------------------------------

    for chunk in llm.stream(prompt):

        if hasattr(chunk, "content"):

            content = chunk.content

        else:

            content = str(chunk)

        if content:

            yield content