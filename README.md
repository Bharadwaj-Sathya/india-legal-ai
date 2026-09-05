# 🇮🇳 India Legal AI

### AI-Powered Indian Legal Knowledge Assistant

> **Understand Indian Law. Backed by Evidence.**

India Legal AI is an evidence-grounded **LLM + Hybrid RAG platform** designed to help users understand the Constitution of India, Indian laws, legal sections, and historical-to-current legal provisions.

The system retrieves relevant provisions from authoritative legal documents, combines semantic and keyword search, reranks the retrieved evidence, and generates concise answers with **source citations**.

> ⚠️ **Disclaimer:** India Legal AI is an informational and research tool. It does not provide legal advice or replace a qualified legal professional.

---

## 🎯 Problem

Indian legal information is extensive, fragmented, and often difficult to understand.

Users may encounter questions such as:

- What is Section 420?
- What is the current equivalent of IPC Section 420?
- What does Article 21 of the Constitution mean?
- What replaced the Indian Penal Code?
- What is the difference between IPC and BNS?
- Which section deals with a particular offence?
- What does a legal provision mean in simple language?

Traditional search engines can return large numbers of documents without providing context or connecting related provisions.

India Legal AI aims to provide a **structured, searchable, and evidence-grounded interface for Indian legal information**.

---

# 🚀 Key Features

### ⚖️ Legal Section Discovery

Search for laws using:

- Act name
- Section number
- Chapter
- Keywords
- Legal concepts

Example:

```text
"What is IPC Section 420?"
```

---

### 🔄 Historical → Current Law Mapping

Connect historical legislation with current legislation.

Example:

```text
IPC Section 420
        ↓
Indian Penal Code, 1860
        ↓
Repealed
        ↓
BNS Section 318(4)
```

This allows users to understand how provisions changed after the introduction of the new criminal laws.

---

### 🔎 Hybrid Search

India Legal AI combines:

```text
Semantic Search
       +
Keyword Search
       ↓
Hybrid Retrieval
       ↓
Reranking
```

This improves retrieval for both natural-language questions and exact legal references.

---

### 📑 Section-Level Retrieval

Legal documents are not treated as generic text.

The ingestion pipeline extracts:

```text
Act
 └── Chapter
      └── Section
           └── Subsection
                └── Clause
```

This allows the system to retrieve precise legal provisions.

---

### 🔗 Evidence & Citations

Answers are grounded in retrieved legal documents.

Example:

```text
Answer

Section 420 of the Indian Penal Code dealt with
cheating and dishonestly inducing delivery of property.

Source:
Indian Penal Code, 1860
Section 420
Page: 123
```

---

### 🛡️ Hallucination Detection

The system verifies generated answers against retrieved evidence.

The objective is:

```text
No Evidence
     ↓
Don't Generate
```

rather than allowing the LLM to confidently invent legal information.

---

### ⚡ Low-Latency Architecture

The system is designed with a target of:

```text
P50 Time-to-First-Token   < 500 ms
P95 Time-to-First-Token   < 1 sec
P95 Retrieval             < 250 ms
Cached Queries            < 100 ms
```

Performance is measured rather than assumed.

---

# 🧠 System Architecture

```text
                         User
                           │
                           ▼
                    ┌─────────────┐
                    │   Next.js   │
                    │   Frontend  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │   Backend   │
                    └──────┬──────┘
                           │
                           ▼
                   ┌────────────────┐
                   │  Query Router  │
                   └───────┬────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Exact Lookup   Hybrid RAG   Complex Query
              │            │            │
              ▼            ▼            ▼
         PostgreSQL    pgvector      Retrieval
                           │             │
                           ▼             ▼
                          BM25       Reranker
                           │             │
                           └──────┬──────┘
                                  │
                                  ▼
                              Context
                                  │
                                  ▼
                               LLM
                                  │
                                  ▼
                         Evidence Verification
                                  │
                                  ▼
                         Streaming Response
```

---

# 📚 Data Pipeline

Official legal documents are processed offline before they become available to the application.

```text
Official Legal PDFs
        │
        ▼
   PDF Extraction
        │
        ▼
 Legal Structure Parser
        │
        ▼
Act / Chapter / Section
        │
        ▼
 Legal-Aware Chunking
        │
        ▼
   Metadata Creation
        │
        ▼
    Embeddings
        │
        ▼
 PostgreSQL + pgvector
```

---

# 📂 Data Sources

Initial knowledge base:

```text
Constitution of India
Bharatiya Nyaya Sanhita, 2023
Bharatiya Nagarik Suraksha Sanhita, 2023
Bharatiya Sakshya Adhiniyam, 2023

Indian Penal Code, 1860
Code of Criminal Procedure, 1973
Indian Evidence Act, 1872

Information Technology Act, 2000
Consumer Protection Act, 2019
Right to Information Act, 2005
Indian Contract Act, 1872
Motor Vehicles Act, 1988
```

Primary sources will be authoritative government legal repositories such as **India Code** and relevant government ministries.

---

# 🏗️ Project Structure

```text
india-legal-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── rag/
│   │   ├── llm/
│   │   ├── database/
│   │   ├── cache/
│   │   └── utils/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── ingestion/
│   ├── sources/
│   ├── pdf/
│   ├── parser/
│   ├── chunking/
│   ├── embeddings/
│   ├── loaders/
│   ├── mappings/
│   └── pipeline.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── evaluation/
│
├── prompts/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
│
├── evaluation/
│   ├── retrieval/
│   ├── generation/
│   └── benchmark.py
│
├── scripts/
│
├── monitoring/
│
├── docs/
│
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

---

# 🛠️ Technology Stack

## Backend

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Pytest

## LLM / AI

- Open-source LLMs
- Ollama
- vLLM
- BGE Embeddings
- BGE Reranker
- LangChain

## Retrieval

- PostgreSQL
- pgvector
- BM25
- Hybrid Retrieval
- Reranking

## Document Processing

- PyMuPDF
- pdfplumber
- Tesseract OCR

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Infrastructure

- PostgreSQL
- Redis
- Docker
- Docker Compose
- GitHub Actions

## Observability

- Langfuse
- Custom latency metrics
- Retrieval evaluation

---

# 🔥 Example Queries

### Section Lookup

```text
What is IPC Section 420?
```

### Current Law Mapping

```text
What is the current equivalent of IPC 420?
```

### Constitution

```text
Explain Article 21 in simple language.
```

### Comparison

```text
What is the difference between IPC and BNS?
```

### Legal Concept

```text
What law deals with cheating in India?
```

### Evidence-Based Question

```text
Show me the relevant legal provisions and explain them.
```

---

# 🔬 RAG Pipeline

The core question-answering pipeline:

```text
User Query
     │
     ▼
Query Classification
     │
     ├── Exact Section Lookup
     │
     ├── Semantic Search
     │
     └── Complex Legal Query
             │
             ▼
       Hybrid Retrieval
             │
       ┌─────┴─────┐
       ▼           ▼
    pgvector      BM25
       │           │
       └─────┬─────┘
             ▼
          Reranker
             │
             ▼
       Top Relevant Evidence
             │
             ▼
       Context Construction
             │
             ▼
            LLM
             │
             ▼
     Evidence Verification
             │
             ▼
       Cited Response
```

---

# 🧩 Query Routing

Not every query needs the full RAG pipeline.

### Simple lookup

```text
"What is Section 420?"

        ↓

Query Router

        ↓

PostgreSQL

        ↓

Section 420

        ↓

Fast Response
```

### Complex question

```text
"Compare IPC 420 with the current BNS provision."

        ↓

Hybrid Retrieval

        ↓

Reranking

        ↓

LLM

        ↓

Evidence-backed answer
```

This reduces unnecessary LLM and retrieval latency.

---

# ⚡ Performance Engineering

India Legal AI is designed around low-latency retrieval and generation.

Key strategies:

- Query routing
- Exact section indexes
- PostgreSQL indexing
- pgvector indexing
- Hybrid retrieval
- Limited reranking candidates
- Redis caching
- Async FastAPI
- Streaming responses
- Local model serving
- vLLM for production inference
- Precomputed embeddings
- Offline document processing

Target:

```text
                    Target

Exact Section       < 100 ms
Cached Query        < 100 ms
Retrieval           < 250 ms
P50 TTFT            < 500 ms
P95 TTFT            < 1 sec
```

---

# 🧪 Evaluation

The system will maintain a dedicated evaluation dataset.

Example:

```json
{
  "question": "What is IPC Section 420?",
  "expected_section": "IPC 420",
  "expected_act": "Indian Penal Code, 1860"
}
```

Evaluation metrics include:

### Retrieval

- Recall@K
- Precision@K
- MRR
- Hit Rate

### Generation

- Answer correctness
- Faithfulness
- Citation accuracy
- Hallucination rate

### Performance

- P50 latency
- P95 latency
- Time to First Token
- Retrieval latency
- LLM latency

---

# 🗺️ Development Roadmap

## Phase 1 — Data Ingestion

- [ ] Collect official PDFs
- [ ] PDF extraction
- [ ] Section detection
- [ ] Chapter detection
- [ ] Metadata extraction
- [ ] Structured JSON generation

## Phase 2 — Database

- [ ] PostgreSQL setup
- [ ] Legal document schema
- [ ] Section indexing
- [ ] pgvector
- [ ] IPC → BNS mappings

## Phase 3 — RAG

- [ ] Embedding generation
- [ ] Vector search
- [ ] BM25 search
- [ ] Hybrid retrieval
- [ ] Reranking
- [ ] Context builder

## Phase 4 — LLM

- [ ] LLM interface
- [ ] Prompt management
- [ ] Grounded generation
- [ ] Citation generation
- [ ] Hallucination detection
- [ ] Streaming

## Phase 5 — API

- [ ] FastAPI
- [ ] Query endpoint
- [ ] Section endpoint
- [ ] Search endpoint
- [ ] Document endpoint

## Phase 6 — Frontend

- [ ] Chat interface
- [ ] Law search
- [ ] Section viewer
- [ ] Citations
- [ ] Law comparison
- [ ] Search history

## Phase 7 — Evaluation

- [ ] Retrieval benchmark
- [ ] Generation benchmark
- [ ] Latency benchmark
- [ ] Hallucination benchmark

## Phase 8 — Deployment

- [ ] Docker
- [ ] Docker Compose
- [ ] CI/CD
- [ ] Monitoring
- [ ] Production deployment

---

# 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/<your-username>/india-legal-ai.git

cd india-legal-ai
```

### Create Python environment

```bash
python -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Configure environment

```bash
cp .env.example .env
```

### Start infrastructure

```bash
docker compose up -d postgres redis
```

### Run backend

```bash
uvicorn backend.app.main:app --reload
```

---

# 🔐 Environment Variables

Example:

```env
APP_ENV=development

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/india_legal_ai

REDIS_URL=redis://localhost:6379

LLM_PROVIDER=ollama

LLM_MODEL=<model-name>

EMBEDDING_MODEL=<embedding-model>

VECTOR_DIMENSION=<dimension>
```

Never commit `.env` files or API keys to GitHub.

---

# 🤝 Engineering Principles

India Legal AI follows:

- SOLID principles
- Object-Oriented Design
- Separation of concerns
- Dependency injection
- Repository pattern
- Service layer architecture
- Configuration management
- Automated testing
- Observability
- Reproducible ingestion
- Evidence-grounded generation

---

# 📈 Future Enhancements

Planned improvements:

- Multilingual Indian language support
- Voice-based legal search
- Legal knowledge graph
- Court judgment retrieval
- Case-law search
- Amendment tracking
- Automatic legal-document updates
- Advanced citation verification
- Personalized learning mode
- Legal timeline visualization

---

# ⚠️ Disclaimer

India Legal AI is an **educational and informational technology project**.

It does not constitute legal advice, legal representation, or a substitute for consultation with a qualified legal professional.

Users should independently verify legal information against current authoritative sources, particularly because laws may be amended, repealed, or replaced.

---

# 👨‍💻 Author

**Bharadwaj Sathya**

AI / ML Engineer

Built with Python, RAG, LLMs, FastAPI, Next.js and modern AI engineering practices.

---

## ⭐ Project Vision

> **Make Indian legal information easier to discover, understand, and verify — without sacrificing the connection to authoritative legal evidence.**