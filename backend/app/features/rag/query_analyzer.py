from __future__ import annotations

import json
import re
from typing import Any

from langchain_ollama import ChatOllama


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "llama3.2"


# ============================================================
# QUERY ANALYSIS PROMPT
# ============================================================

QUERY_ANALYSIS_PROMPT = """
You are a query analyzer for an Indian legal RAG system.

Your job is NOT to answer the user's legal question.

Your job is to understand the query and convert it into structured
search information that can be used to retrieve relevant legal
documents.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{
  "intent": "string",
  "act": "string or null",
  "section": "string or null",
  "search_query": "string",
  "keywords": ["string"]
}

Possible intents include:

- section_lookup
- legal_rights
- punishment
- definition
- procedure
- bail
- arrest
- investigation
- offence
- property
- evidence
- general_legal_question

Act values must use these internal identifiers when identifiable:

- ipc_1860
- crpc_1973
- transfer_of_property_act
- indian_evidence_act
- constitution_of_india

If the Act cannot be determined, return null.

If the user asks about a specific section, extract the section number.

Examples:

User:
"What is Section 420?"

Output:
{
  "intent": "section_lookup",
  "act": "ipc_1860",
  "section": "420",
  "search_query": "Section 420 cheating dishonestly inducing delivery of property",
  "keywords": [
    "section 420",
    "cheating",
    "dishonestly inducing delivery of property"
  ]
}

User:
"What are my rights if I am arrested?"

Output:
{
  "intent": "legal_rights",
  "act": "crpc_1973",
  "section": null,
  "search_query": "rights of arrested person arrest police custody detention accused",
  "keywords": [
    "arrest",
    "arrested person",
    "rights",
    "custody",
    "detention",
    "accused",
    "police",
    "magistrate",
    "legal counsel"
  ]
}

User:
"What is the punishment for theft?"

Output:
{
  "intent": "punishment",
  "act": "ipc_1860",
  "section": null,
  "search_query": "punishment for theft stealing property",
  "keywords": [
    "theft",
    "punishment",
    "stealing",
    "property"
  ]
}

IMPORTANT:

- Correct obvious spelling mistakes.
- Understand the meaning rather than matching exact words.
- Do not answer the legal question.
- Do not invent a section number.
- Do not invent an Act.
- If uncertain, use null.
- Return JSON only.
"""


# ============================================================
# LLM
# ============================================================

def create_query_analyzer(
    model: str = DEFAULT_MODEL,
) -> ChatOllama:
    """
    Create Ollama model used for query analysis.
    """

    return ChatOllama(
        model=model,
        temperature=0,
    )


# ============================================================
# JSON EXTRACTION
# ============================================================

def _extract_json(
    text: str,
) -> dict[str, Any]:
    """
    Extract JSON from the Ollama response.

    Handles responses where the model accidentally wraps
    JSON in markdown code fences.
    """

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Find JSON object inside response
    # --------------------------------------------------------

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if match:

        try:

            result = json.loads(
                match.group(0)
            )

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Ollama returned invalid query-analysis JSON."
    )


# ============================================================
# FALLBACK SECTION EXTRACTION
# ============================================================

def _fallback_section(
    query: str,
) -> str | None:

    match = re.search(
        r"\b(?:section|sec\.?|s\.?)\s*(\d+[A-Za-z]?)\b",
        query,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# QUERY ANALYSIS
# ============================================================

def analyze_query(
    query: str,
    llm: ChatOllama | None = None,
) -> dict[str, Any]:
    """
    Ask Ollama to understand the user's legal query.

    Returns structured search information.
    """

    if llm is None:
        llm = create_query_analyzer()

    prompt = (
        QUERY_ANALYSIS_PROMPT
        + "\n\nUser query:\n"
        + query
        + "\n\nJSON:"
    )

    response = llm.invoke(prompt)

    analysis = _extract_json(
        response.content
    )

    # --------------------------------------------------------
    # Ensure expected fields exist
    # --------------------------------------------------------

    result = {
        "intent": analysis.get(
            "intent",
            "general_legal_question",
        ),
        "act": analysis.get(
            "act"
        ),
        "section": analysis.get(
            "section"
        ),
        "search_query": analysis.get(
            "search_query",
            query,
        ),
        "keywords": analysis.get(
            "keywords",
            [],
        ),
    }

    # --------------------------------------------------------
    # Normalize values
    # --------------------------------------------------------

    if result["act"] == "null":
        result["act"] = None

    if result["section"] == "null":
        result["section"] = None

    if not isinstance(
        result["keywords"],
        list,
    ):
        result["keywords"] = []

    # --------------------------------------------------------
    # Safety fallback for section extraction
    # --------------------------------------------------------

    if result["section"] is None:

        fallback_section = _fallback_section(
            query
        )

        if fallback_section:
            result["section"] = (
                fallback_section
            )

    return result