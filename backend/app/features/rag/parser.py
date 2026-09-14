from __future__ import annotations

import re
from typing import Iterable

from langchain_core.documents import Document


# ============================================================
# REGEX
# ============================================================

# Normal section heading:
#
# 420. Cheating...
# 57. Person arrested...
# 50A. Obligation...
#
SECTION_HEADING_PATTERN = re.compile(
    r"""^[ \t]*["']?(\d+[A-Za-z]?)[.)\-:][ \t]+(.+?)["']?[ \t]*$"""
)


# Isolated section number:
#
# 57.
#
ISOLATED_SECTION_PATTERN = re.compile(
    r"^[ \t]*(\d+[A-Za-z]?)[.)\-:][ \t]*$"
)


# Amendment item:
#
# 7. Insertion of new section 50A.-
# 8. Amendment of section 53.
#
AMENDMENT_ITEM_PATTERN = re.compile(
    r"""^[ \t]*\d+[.)\-:][ \t]+
        (?:
            insertion\s+of
            |
            amendment\s+of
            |
            substitution\s+of
            |
            omission\s+of
            |
            repeal\s+of
            |
            renumbering\s+of
        )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# Quoted inserted section:
#
# "50A. Obligation of person making arrest...
#
QUOTED_SECTION_PATTERN = re.compile(
    r"""^[ \t]*["'](\d+[A-Za-z]?)[.)\-:][ \t]+(.+)$"""
)


# Table of contents:
#
# 779-420 Cheating...
#
TOC_PATTERN = re.compile(
    r"^\s*\d+\s*-\s*\d+[A-Za-z]?\b"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_line(line: str) -> str:
    """
    Normalize PDF whitespace.
    """

    line = line.replace("\u00a0", " ")

    line = re.sub(
        r"[ \t]+",
        " ",
        line,
    )

    return line.strip()


def is_toc_line(line: str) -> bool:
    return bool(
        TOC_PATTERN.match(line)
    )


def is_amendment_item(line: str) -> bool:
    return bool(
        AMENDMENT_ITEM_PATTERN.match(line)
    )


def extract_amendment_target(
    line: str,
) -> str | None:
    """
    Extract the target section from:

        7. Insertion of new section 50A.-
        8. Amendment of section 53.
    """

    match = re.search(
        r"(?:new\s+)?section\s+(\d+[A-Za-z]?)",
        line,
        re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1)


def is_section_reference(line: str) -> bool:
    """
    Reject:

        Section 420 of the principal Act
        section 50 of this Act
    """

    return bool(
        re.match(
            r"^section\s+\d+[A-Za-z]?\b",
            line,
            re.IGNORECASE,
        )
    )


# ============================================================
# SECTION DETECTION
# ============================================================

def extract_section_heading(
    line: str,
) -> tuple[str, str] | None:
    """
    Detect normal legal section headings.

    Examples:

        420. Cheating...
        57. Person arrested...
        50A. Obligation...
    """

    line = clean_line(line)

    if not line:
        return None

    if is_toc_line(line):
        return None

    if is_amendment_item(line):
        return None

    if is_section_reference(line):
        return None

    match = SECTION_HEADING_PATTERN.match(line)

    if not match:
        return None

    section = match.group(1).strip()
    title = match.group(2).strip()

    if not section or not title:
        return None

    return section, title


def extract_quoted_section(
    line: str,
) -> tuple[str, str] | None:
    """
    Detect inserted sections such as:

        "50A. Obligation of person making arrest...
    """

    line = clean_line(line)

    match = QUOTED_SECTION_PATTERN.match(line)

    if not match:
        return None

    section = match.group(1).strip()
    title = match.group(2).strip()

    # Remove trailing quote caused by PDF extraction.
    title = title.rstrip('"').rstrip("'").strip()

    if not section or not title:
        return None

    return section, title


# ============================================================
# METADATA
# ============================================================

def enrich_metadata(
    documents: Iterable[Document],
    category: str,
    act_name: str,
    source_file: str,
) -> list[Document]:
    """
    Add common metadata to each PDF page.
    """

    enriched: list[Document] = []

    for page_number, document in enumerate(
        documents,
        start=1,
    ):

        metadata = dict(
            document.metadata or {}
        )

        metadata.update(
            {
                "category": category,
                "act": act_name,
                "source_file": source_file,
                "page": page_number,
            }
        )

        enriched.append(
            Document(
                page_content=document.page_content,
                metadata=metadata,
            )
        )

    return enriched


# ============================================================
# LEGAL SECTION PARSER
# ============================================================

def parse_legal_sections(
    documents: list[Document],
) -> list[Document]:
    """
    Parse PDF pages into legal sections.

    IMPORTANT:

    Section state is maintained ACROSS PDF pages.

    Example:

        Page 30:
            57. Person arrested...
            ...

        Page 31:
            continuation...

    Both remain Section 57.

    Amendment example:

        7. Insertion of new section 50A.-
        "50A. Obligation of person making arrest...
        (1) ...
        (2) ...
        (3) ...
        (4) ...

    The amendment item 7 is NOT treated as Section 7.
    """

    parsed: list[Document] = []

    # --------------------------------------------------------
    # Current legal section state
    # --------------------------------------------------------

    current_section: str | None = None
    current_title: str | None = None

    current_lines: list[str] = []

    current_start_page: int | None = None
    current_end_page: int | None = None

    current_amendment_item: str | None = None
    current_amendment_target: str | None = None

    # --------------------------------------------------------
    # Pending amendment information
    # --------------------------------------------------------

    pending_amendment_lines: list[str] = []
    pending_amendment_item: str | None = None
    pending_amendment_target: str | None = None

    def flush_current() -> None:
        """
        Store the current section.
        """

        nonlocal current_lines
        nonlocal current_section
        nonlocal current_title
        nonlocal current_start_page
        nonlocal current_end_page
        nonlocal current_amendment_item
        nonlocal current_amendment_target

        if not current_lines:
            return

        content = "\n".join(
            current_lines
        ).strip()

        if not content:
            current_lines = []
            return

        # Only create legal section documents
        # when a section number exists.
        if current_section:

            metadata = {}

            # We don't use the page metadata from only
            # the last line. Instead preserve useful fields.
            if documents:
                first_metadata = (
                    documents[0].metadata or {}
                )
                metadata.update(first_metadata)

            metadata["section"] = current_section

            if current_title:
                metadata["section_title"] = (
                    current_title
                )

            if current_start_page is not None:
                metadata["page"] = (
                    current_start_page
                )

            if current_start_page is not None:
                metadata["start_page"] = (
                    current_start_page
                )

            if current_end_page is not None:
                metadata["end_page"] = (
                    current_end_page
                )

            if current_amendment_item:
                metadata["amendment_item"] = (
                    current_amendment_item
                )

            if current_amendment_target:
                metadata["amendment_target_section"] = (
                    current_amendment_target
                )

            metadata["is_legal_section"] = True

            parsed.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )

        current_lines = []

    # --------------------------------------------------------
    # Iterate through ALL pages
    # --------------------------------------------------------

    for document in documents:

        text = document.page_content or ""

        if not text.strip():
            continue

        page_metadata = dict(
            document.metadata or {}
        )

        page_number = page_metadata.get(
            "page"
        )

        lines = [
            clean_line(line)
            for line in text.splitlines()
        ]

        i = 0

        while i < len(lines):

            line = lines[i]

            # ------------------------------------------------
            # Empty line
            # ------------------------------------------------

            if not line:

                if current_lines:
                    current_lines.append("")

                i += 1
                continue

            # ------------------------------------------------
            # Table of contents
            # ------------------------------------------------

            if is_toc_line(line):

                # Do not allow TOC entries to become
                # legal section headings.
                i += 1
                continue

            # ------------------------------------------------
            # Amendment item
            # ------------------------------------------------

            if is_amendment_item(line):

                amendment_match = re.match(
                    r"^(\d+)[.)\-:]\s*(.+)$",
                    line,
                )

                if amendment_match:

                    pending_amendment_item = (
                        amendment_match.group(1)
                    )

                    pending_amendment_target = (
                        extract_amendment_target(
                            line
                        )
                    )

                    pending_amendment_lines = [
                        line
                    ]

                i += 1
                continue

            # ------------------------------------------------
            # Quoted inserted section
            # ------------------------------------------------

            quoted_heading = extract_quoted_section(
                line
            )

            if quoted_heading and (
                pending_amendment_item
                or pending_amendment_target
            ):

                section_number, section_title = (
                    quoted_heading
                )

                # New legal section.
                flush_current()

                current_section = section_number
                current_title = section_title

                current_start_page = page_number
                current_end_page = page_number

                current_amendment_item = (
                    pending_amendment_item
                )

                current_amendment_target = (
                    pending_amendment_target
                )

                # Preserve amendment instruction as
                # context for this inserted section.
                current_lines = []

                if pending_amendment_lines:
                    current_lines.extend(
                        pending_amendment_lines
                    )

                current_lines.append(line)

                pending_amendment_lines = []
                pending_amendment_item = None
                pending_amendment_target = None

                i += 1
                continue

            # ------------------------------------------------
            # Isolated section number
            #
            # Example:
            #
            # 57.
            #
            # Person arrested not to be detained...
            # ------------------------------------------------

            isolated_match = (
                ISOLATED_SECTION_PATTERN.match(line)
            )

            if isolated_match:

                section_number = (
                    isolated_match.group(1)
                )

                # Look ahead for title.
                j = i + 1

                while (
                    j < len(lines)
                    and not lines[j]
                ):
                    j += 1

                if j < len(lines):

                    possible_title = lines[j]

                    if (
                        possible_title
                        and not is_toc_line(
                            possible_title
                        )
                        and not is_section_reference(
                            possible_title
                        )
                    ):

                        flush_current()

                        current_section = (
                            section_number
                        )

                        current_title = (
                            possible_title
                        )

                        current_start_page = (
                            page_number
                        )

                        current_end_page = (
                            page_number
                        )

                        current_amendment_item = None
                        current_amendment_target = None

                        current_lines = [
                            f"{section_number}. "
                            f"{possible_title}"
                        ]

                        i = j + 1
                        continue

            # ------------------------------------------------
            # Normal section heading
            # ------------------------------------------------

            normal_heading = extract_section_heading(
                line
            )

            if normal_heading:

                section_number, section_title = (
                    normal_heading
                )

                flush_current()

                current_section = section_number
                current_title = section_title

                current_start_page = page_number
                current_end_page = page_number

                current_amendment_item = None
                current_amendment_target = None

                current_lines = [
                    line
                ]

                i += 1
                continue

            # ------------------------------------------------
            # Normal content
            # ------------------------------------------------

            # If an amendment instruction occurred but
            # no inserted section was found yet, retain it.
            if pending_amendment_lines:
                pending_amendment_lines.append(
                    line
                )

            elif current_section:

                current_lines.append(line)

                if page_number is not None:
                    current_end_page = page_number

            i += 1

    # --------------------------------------------------------
    # Flush final section
    # --------------------------------------------------------

    flush_current()

    # --------------------------------------------------------
    # Final metadata
    # --------------------------------------------------------

    final_documents: list[Document] = []

    for index, document in enumerate(parsed):

        metadata = dict(
            document.metadata or {}
        )

        metadata["chunk_id"] = index
        metadata["is_legal_section"] = True

        final_documents.append(
            Document(
                page_content=document.page_content,
                metadata=metadata,
            )
        )

    return final_documents


# ============================================================
# DEBUG
# ============================================================

def find_section_candidates(
    text: str,
) -> list[dict[str, str]]:
    """
    Debug helper for inspecting section detection.
    """

    results: list[dict[str, str]] = []

    lines = [
        clean_line(line)
        for line in text.splitlines()
    ]

    for line in lines:

        heading = extract_section_heading(
            line
        )

        if heading:

            section, title = heading

            results.append(
                {
                    "section": section,
                    "title": title,
                    "line": line,
                }
            )

    return results