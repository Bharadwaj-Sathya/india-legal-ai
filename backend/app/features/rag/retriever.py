from __future__ import annotations

from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.features.rag.query_analyzer import analyze_query


# ============================================================
# INTENT PROFILES
# ============================================================

INTENT_PROFILES: dict[str, dict[str, list[str]]] = {
    "arrest_rights": {
        "keywords": [
            "arrest",
            "arrested",
            "rights",
            "grounds of arrest",
            "bail",
            "detention",
            "custody",
            "police",
            "magistrate",
            "nominated person",
            "inform",
            "inform arrested person",
            "legal practitioner",
            "medical examination",
        ],
        "priority_sections": [
            "50",
            "50A",
            "57",
            "54",
            "56",
            "50",
            "41A",
            "41",
            "46",
            "167",
            "436",
            "437",
            "438",
        ],
    },

    "bail": {
        "keywords": [
            "bail",
            "release",
            "bond",
            "sureties",
            "bailable",
            "non-bailable",
            "custody",
        ],
        "priority_sections": [
            "436",
            "437",
            "438",
            "439",
            "440",
        ],
    },

    "cheating": {
        "keywords": [
            "cheating",
            "dishonestly",
            "property",
            "delivery",
            "fraud",
            "deception",
        ],
        "priority_sections": [
            "415",
            "416",
            "417",
            "418",
            "419",
            "420",
        ],
    },

    "theft": {
        "keywords": [
            "theft",
            "dishonestly",
            "movable property",
            "possession",
            "property",
        ],
        "priority_sections": [
            "378",
            "379",
            "380",
            "381",
            "382",
        ],
    },

    "murder": {
        "keywords": [
            "murder",
            "death",
            "intention",
            "knowledge",
            "causing death",
            "culpable homicide",
        ],
        "priority_sections": [
            "299",
            "300",
            "301",
            "302",
            "304",
        ],
    },
}


# ============================================================
# BASIC RETRIEVER
# ============================================================

def create_retriever(
    vectorstore: Chroma,
    k: int = 5,
):
    """
    Create the default LangChain similarity retriever.

    This function is kept for compatibility with the rest of
    the application.
    """

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


# ============================================================
# EXACT SECTION SEARCH
# ============================================================

def section_search(
    vectorstore: Chroma,
    section: str,
    k: int = 5,
    act: str | None = None,
) -> list[Document]:
    """
    Retrieve documents belonging to an exact legal section.

    If an Act is provided, both section and Act are filtered.
    """

    section = str(section).strip()

    if act:
        where = {
            "$and": [
                {"section": section},
                {"act": act},
            ]
        }
    else:
        where = {
            "section": section,
        }

    results = vectorstore.get(where=where)

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    output: list[Document] = []

    for index, content in enumerate(documents):
        metadata: dict[str, Any] = {}

        if index < len(metadatas):
            metadata = metadatas[index] or {}

        output.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return output[:k]


# ============================================================
# KEYWORD SCORE
# ============================================================

def keyword_score(
    document: Document,
    keywords: list[str],
) -> float:
    """
    Score a document based on keyword matches.

    Section title matches are intentionally weighted much more
    heavily than ordinary content matches.

    Example:

        "Person arrested to be informed of grounds of arrest
         and of right to bail."

    should receive a strong score for an arrest-rights query.
    """

    if not keywords:
        return 0.0

    content = (document.page_content or "").lower()

    metadata = document.metadata or {}

    title = str(
        metadata.get("section_title", "")
    ).lower()

    score = 0.0

    for keyword in keywords:

        keyword = str(keyword).lower().strip()

        if not keyword:
            continue

        # Strong signal:
        # keyword appears in the section title.
        if keyword in title:
            score += 8.0

        # Weaker signal:
        # keyword appears somewhere in the section content.
        if keyword in content:
            score += 0.75

    return score


# ============================================================
# INTENT SCORE
# ============================================================

def intent_score(
    document: Document,
    intent: str | None,
) -> float:
    """
    Give sections an intent-specific priority.

    Arrest-rights questions use a manually ordered priority
    because not every arrest-related section is equally useful.

    For example:

        Section 50  -> very important
        Section 50A -> very important
        Section 57  -> important
        Section 81  -> low priority because it concerns a
                       warrant-arrest procedure.
    """

    if not intent:
        return 0.0

    metadata = document.metadata or {}

    section = str(
        metadata.get("section", "")
    ).strip()

    # --------------------------------------------------------
    # ARREST RIGHTS
    # --------------------------------------------------------

    if intent == "arrest_rights":

        priority = {
            "50": 15.0,
            "50A": 14.0,
            "57": 10.0,
            "54": 8.0,
            "56": 7.0,
            "41A": 6.0,
            "41": 5.0,
            "46": 3.0,
            "167": 3.0,
            "436": 3.0,
            "437": 3.0,
            "438": 3.0,

            # Section 81 is mainly relevant when the arrest
            # relates to a warrant.
            "81": 0.5,
        }

        return priority.get(section, 0.0)

    # --------------------------------------------------------
    # OTHER INTENTS
    # --------------------------------------------------------

    profile = INTENT_PROFILES.get(intent)

    if not profile:
        return 0.0

    priority_sections = profile.get(
        "priority_sections",
        [],
    )

    if section in priority_sections:
        return 5.0

    return 0.0


# ============================================================
# ACT SCORE
# ============================================================

def act_score(
    document: Document,
    act: str | None,
) -> float:
    """
    Give a small additional score when the document belongs
    to the requested Act.

    Actual Act filtering is still performed in Chroma when
    possible. This score is an additional ranking signal.
    """

    if not act:
        return 0.0

    metadata = document.metadata or {}

    document_act = str(
        metadata.get("act", "")
    ).strip()

    if document_act.lower() == act.lower():
        return 2.0

    return 0.0


# ============================================================
# DIRECT CONTENT SCORE
# ============================================================

def direct_content_score(
    document: Document,
    intent: str | None,
) -> float:
    """
    Detect strong phrases directly related to the intent.

    These are additional ranking signals and do not replace
    semantic search.
    """

    content = (
        document.page_content or ""
    ).lower()

    metadata = document.metadata or {}

    title = str(
        metadata.get("section_title", "")
    ).lower()

    # Combine title + content so important legal headings
    # also contribute.
    searchable_text = f"{title} {content}"

    # --------------------------------------------------------
    # ARREST RIGHTS
    # --------------------------------------------------------

    if intent == "arrest_rights":

        score = 0.0

        strong_phrases = [
            "person arrested",
            "arrested person",
            "grounds of arrest",
            "right to bail",
            "entitled to be released on bail",
            "inform the arrested person",
            "inform the person arrested",
            "nominated person",
            "nominated person about the arrest",
            "not be detained",
            "twenty-four hours",
            "24 hours",
            "before a magistrate",
            "produced before a magistrate",
            "medical practitioner",
            "examination of arrested person",
            "examination of the body",
        ]

        for phrase in strong_phrases:

            if phrase in searchable_text:
                score += 2.0

        return score

    return 0.0


# ============================================================
# LEGAL RELEVANCE SCORE
# ============================================================

def legal_relevance_score(
    document: Document,
    intent: str | None,
    keywords: list[str],
    act: str | None,
    semantic_rank: int,
) -> float:
    """
    Combine multiple ranking signals.

    Score components:

        1. semantic similarity rank
        2. keyword matches
        3. intent-specific section priority
        4. Act match
        5. direct legal phrase match
    """

    # Semantic rank signal.
    semantic_score = 1.0 / (
        semantic_rank + 1
    )

    keywords_score = keyword_score(
        document=document,
        keywords=keywords,
    )

    intent_relevance = intent_score(
        document=document,
        intent=intent,
    )

    act_relevance = act_score(
        document=document,
        act=act,
    )

    direct_score = direct_content_score(
        document=document,
        intent=intent,
    )

    total_score = (
        semantic_score
        + keywords_score * 0.6
        + intent_relevance
        + act_relevance
        + direct_score
    )

    return total_score


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_by_section(
    documents: list[Document],
    max_per_section: int = 1,
) -> list[Document]:
    """
    Keep at most N documents from each legal section.

    This prevents results such as:

        56
        81
        56
        81
        57

    and instead gives broader section coverage.
    """

    output: list[Document] = []

    section_counts: dict[str, int] = {}

    for document in documents:

        metadata = document.metadata or {}

        section = str(
            metadata.get("section", "")
        ).strip()

        # Documents without section metadata are retained.
        if not section:
            output.append(document)
            continue

        count = section_counts.get(
            section,
            0,
        )

        if count >= max_per_section:
            continue

        section_counts[section] = count + 1

        output.append(document)

    return output


# ============================================================
# MAIN LEGAL RETRIEVER
# ============================================================

def retrieve(
    vectorstore: Chroma,
    query: str,
    k: int = 5,
    filter: dict[str, Any] | None = None,
) -> list[Document]:
    """
    Intent-aware legal retrieval.

    Pipeline:

        User query
            ↓
        Query analysis
            ↓
        Exact section search
            ↓
        Semantic candidate retrieval
            ↓
        Legal reranking
            ↓
        Section deduplication
            ↓
        Final top-k documents
    """

    # ========================================================
    # 1. ANALYZE QUERY
    # ========================================================

    analysis = analyze_query(query)

    intent = analysis.get("intent")

    analyzed_act = analysis.get("act")

    section = analysis.get("section")

    search_query = analysis.get(
        "search_query",
        query,
    )

    analyzer_keywords = analysis.get(
        "keywords",
        [],
    )

    # ========================================================
    # 2. DETERMINE ACT
    # ========================================================

    act = analyzed_act

    # Explicit API filter takes priority.
    if filter and "act" in filter:
        act = filter["act"]

    # ========================================================
    # 3. BUILD KEYWORD LIST
    # ========================================================

    profile = INTENT_PROFILES.get(
        intent,
        {
            "keywords": [],
            "priority_sections": [],
        },
    )

    intent_keywords = profile.get(
        "keywords",
        [],
    )

    keywords = list(
        dict.fromkeys(
            [
                *analyzer_keywords,
                *intent_keywords,
            ]
        )
    )

    # ========================================================
    # 4. DEBUG QUERY ANALYSIS
    # ========================================================

    print()

    print("=" * 70)
    print("LEGAL QUERY ANALYSIS")
    print("=" * 70)

    print(
        f"Original query : {query}"
    )

    print(
        f"Intent         : {intent}"
    )

    print(
        f"Act            : {act}"
    )

    print(
        f"Section        : {section}"
    )

    print(
        f"Search query   : {search_query}"
    )

    print(
        f"Keywords       : {keywords}"
    )

    print("=" * 70)

    # ========================================================
    # 5. EXACT SECTION SEARCH
    # ========================================================

    if section:

        exact_results = section_search(
            vectorstore=vectorstore,
            section=str(section),
            k=k,
            act=act,
        )

        if exact_results:

            print(
                f"Exact section match: {section}"
            )

            return exact_results

    # ========================================================
    # 6. SEMANTIC CANDIDATE RETRIEVAL
    # ========================================================

    # Retrieve a larger pool than the final k.

    # Example:
    #
    # final k = 5
    # candidate pool = 50
    #
    # This gives the reranker enough candidates to find
    # important legal provisions that may not initially be
    # in the top 5 semantic results.

    candidate_k = max(
        k * 10,
        40,
    )

    search_kwargs: dict[str, Any] = {
        "k": candidate_k,
    }

    # ========================================================
    # 7. ACT FILTER
    # ========================================================

    if filter:

        search_kwargs["filter"] = filter

    elif act:

        search_kwargs["filter"] = {
            "act": act,
        }

    # ========================================================
    # 8. SEMANTIC SEARCH
    # ========================================================

    semantic_results = (
        vectorstore.similarity_search(
            search_query,
            **search_kwargs,
        )
    )

    if not semantic_results:
        print(
            "No semantic retrieval results."
        )

        return []

    # ========================================================
    # 9. RERANK
    # ========================================================

    scored: list[
        tuple[float, Document]
    ] = []

    for rank, document in enumerate(
        semantic_results
    ):

        score = legal_relevance_score(
            document=document,
            intent=intent,
            keywords=keywords,
            act=act,
            semantic_rank=rank,
        )

        scored.append(
            (
                score,
                document,
            )
        )

    # Highest score first.

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    # ========================================================
    # 10. DEBUG RERANKING
    # ========================================================

    print()

    print("=" * 70)
    print("LEGAL RERANKING")
    print("=" * 70)

    for rank, (
        score,
        document,
    ) in enumerate(
        scored[:20],
        start=1,
    ):

        metadata = (
            document.metadata or {}
        )

        print(
            f"{rank}. "
            f"score={score:.3f} "
            f"section={metadata.get('section')} "
            f"title={metadata.get('section_title', '')} "
            f"act={metadata.get('act')}"
        )

    print("=" * 70)

    # ========================================================
    # 11. EXTRACT RANKED DOCUMENTS
    # ========================================================

    ranked_documents = [
        document
        for _, document in scored
    ]

    # ========================================================
    # 12. SECTION-LEVEL DEDUPLICATION
    # ========================================================

    unique_sections = (
        deduplicate_by_section(
            ranked_documents,
            max_per_section=1,
        )
    )

    # ========================================================
    # 13. FILL REMAINING SLOTS
    # ========================================================

    if len(unique_sections) < k:

        selected_keys = set()

        for document in unique_sections:

            metadata = (
                document.metadata or {}
            )

            key = (
                str(
                    metadata.get(
                        "source_file",
                        "",
                    )
                ),
                str(
                    metadata.get(
                        "section",
                        "",
                    )
                ),
                str(
                    metadata.get(
                        "chunk_id",
                        "",
                    )
                ),
            )

            selected_keys.add(key)

        for _, document in scored:

            metadata = (
                document.metadata or {}
            )

            key = (
                str(
                    metadata.get(
                        "source_file",
                        "",
                    )
                ),
                str(
                    metadata.get(
                        "section",
                        "",
                    )
                ),
                str(
                    metadata.get(
                        "chunk_id",
                        "",
                    )
                ),
            )

            if key in selected_keys:
                continue

            unique_sections.append(
                document
            )

            selected_keys.add(key)

            if len(unique_sections) >= k:
                break

    # ========================================================
    # 14. FINAL RESULTS
    # ========================================================

    final_documents = unique_sections[:k]

    print()

    print("=" * 70)
    print("FINAL RETRIEVAL")
    print("=" * 70)

    for index, document in enumerate(
        final_documents,
        start=1,
    ):

        metadata = (
            document.metadata or {}
        )

        print(
            f"{index}. "
            f"section={metadata.get('section')} "
            f"title={metadata.get('section_title', '')} "
            f"act={metadata.get('act')}"
        )

    print("=" * 70)

    return final_documents


# ============================================================
# SIMPLE SIMILARITY SEARCH
# ============================================================

def similarity_search(
    vectorstore: Chroma,
    query: str,
    k: int = 5,
):
    """
    Compatibility helper.

    Performs plain vector similarity search without the
    legal reranking pipeline.
    """

    return vectorstore.similarity_search(
        query,
        k=k,
    )