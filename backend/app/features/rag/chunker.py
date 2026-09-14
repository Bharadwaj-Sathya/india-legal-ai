from __future__ import annotations

import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# SUBSECTION DETECTION
# ============================================================

SUBSECTION_PATTERN = re.compile(
    r"(?m)^(?P<number>\(\d+[A-Za-z]*\))"
)


# ============================================================
# TEXT SPLITTER
# ============================================================

def create_text_splitter(
    chunk_size: int = 1600,
    chunk_overlap: int = 150,
) -> RecursiveCharacterTextSplitter:
    """
    General fallback splitter.

    1600 characters is intentionally larger than the previous
    700-character setting so normal legal provisions such as
    Section 50A are less likely to be unnecessarily fragmented.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "; ",
            ", ",
            " ",
            "",
        ],
    )


# ============================================================
# SUBSECTION SPLITTER
# ============================================================

def split_into_subsections(
    text: str,
) -> list[str]:
    """
    Split a legal section at subsection boundaries.

    Example:

        Section 50A

        (1) ...
        (2) ...
        (3) ...
        (4) ...

    becomes:

        [
            heading + (1),
            (2),
            (3),
            (4)
        ]

    This prevents arbitrary character-based splitting
    from destroying legal structure.
    """

    matches = list(
        SUBSECTION_PATTERN.finditer(text)
    )

    if not matches:
        return [text.strip()]

    parts: list[str] = []

    # --------------------------------------------------------
    # Text before first subsection
    # --------------------------------------------------------

    first_start = matches[0].start()

    if first_start > 0:

        heading = text[
            :first_start
        ].strip()

        if heading:
            parts.append(
                heading
            )

    # --------------------------------------------------------
    # Individual subsections
    # --------------------------------------------------------

    for index, match in enumerate(matches):

        start = match.start()

        if index + 1 < len(matches):
            end = matches[
                index + 1
            ].start()
        else:
            end = len(text)

        subsection = text[
            start:end
        ].strip()

        if subsection:
            parts.append(
                subsection
            )

    return parts


# ============================================================
# METADATA
# ============================================================

def copy_metadata(
    document: Document,
) -> dict:
    """
    Copy document metadata safely.
    """

    return dict(
        document.metadata or {}
    )


# ============================================================
# CREATE LEGAL CHUNKS
# ============================================================

def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1600,
    chunk_overlap: int = 150,
) -> list[Document]:
    """
    Legal-aware chunking.

    Strategy:

        Section
            ↓
        Subsections
            ↓
        Pack subsections together
            ↓
        Split oversized subsection only if necessary

    Important metadata such as:

        act
        section
        section_title
        category
        source_file
        page
        start_page
        end_page

    is preserved.
    """

    splitter = create_text_splitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    final_chunks: list[Document] = []

    # --------------------------------------------------------
    # Process each legal section
    # --------------------------------------------------------

    for document in documents:

        metadata = copy_metadata(
            document
        )

        text = document.page_content.strip()

        if not text:
            continue

        section = metadata.get(
            "section"
        )

        # ----------------------------------------------------
        # Non-section fallback
        # ----------------------------------------------------

        if not section:

            split_docs = splitter.create_documents(
                [text],
                metadatas=[metadata],
            )

            for split_doc in split_docs:

                final_chunks.append(
                    split_doc
                )

            continue

        # ----------------------------------------------------
        # Split section into subsections
        # ----------------------------------------------------

        subsections = split_into_subsections(
            text
        )

        # ----------------------------------------------------
        # Pack subsections
        # ----------------------------------------------------

        current_parts: list[str] = []
        current_length = 0

        def flush_current():

            nonlocal current_parts
            nonlocal current_length

            if not current_parts:
                return

            content = "\n\n".join(
                current_parts
            ).strip()

            if content:

                chunk_metadata = dict(
                    metadata
                )

                chunk_metadata[
                    "section"
                ] = section

                chunk_metadata[
                    "is_legal_section"
                ] = True

                final_chunks.append(
                    Document(
                        page_content=content,
                        metadata=chunk_metadata,
                    )
                )

            current_parts = []
            current_length = 0

        for subsection in subsections:

            subsection_length = len(
                subsection
            )

            # ------------------------------------------------
            # Normal subsection fits
            # ------------------------------------------------

            if (
                current_length
                + subsection_length
                + 2
                <= chunk_size
            ):

                current_parts.append(
                    subsection
                )

                current_length += (
                    subsection_length
                    + 2
                )

                continue

            # ------------------------------------------------
            # Current chunk full
            # ------------------------------------------------

            flush_current()

            # ------------------------------------------------
            # Oversized subsection
            # ------------------------------------------------

            if subsection_length > chunk_size:

                oversized_docs = (
                    splitter.create_documents(
                        [subsection],
                        metadatas=[
                            metadata
                        ],
                    )
                )

                for oversized_doc in oversized_docs:

                    oversized_metadata = dict(
                        oversized_doc.metadata
                        or {}
                    )

                    oversized_metadata[
                        "section"
                    ] = section

                    oversized_metadata[
                        "is_legal_section"
                    ] = True

                    final_chunks.append(
                        Document(
                            page_content=(
                                oversized_doc.page_content
                            ),
                            metadata=(
                                oversized_metadata
                            ),
                        )
                    )

            else:

                current_parts = [
                    subsection
                ]

                current_length = (
                    subsection_length
                )

        flush_current()

    # ========================================================
    # ASSIGN CHUNK IDS
    # ========================================================

    output: list[Document] = []

    for index, document in enumerate(
        final_chunks
    ):

        metadata = dict(
            document.metadata or {}
        )

        metadata["chunk_id"] = index

        output.append(
            Document(
                page_content=document.page_content,
                metadata=metadata,
            )
        )

    return output