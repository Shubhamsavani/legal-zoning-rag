# Intelli-Site — Provenance-Aware Legal RAG for NYC Zoning Analysis

## Overview

Intelli-Site is a legal Retrieval-Augmented Generation (RAG) system designed for NYC zoning and land-use analysis.

The system combines:

* structured site records
* zoning regulation retrieval
* local LLM reasoning
* deterministic provenance-aware citations
* evaluation and hallucination safeguards

The goal is to build a legally cautious AI assistant that can answer zoning-related questions while grounding responses in retrieved regulatory text and structured parcel data.

---

# Key Features

## Provenance-Aware Legal RAG

Every retrieved zoning chunk contains:

* source file
* section title
* amendment date
* exact line ranges

Responses include deterministic citations generated from retrieval metadata rather than hallucinated by the LLM.

Example:

```text
Rear yard requirements are discussed in
Section 23-342
[zr_03_rear_yard_requirements.md | lines 2-23]
```

---

## Legal-Specific Chunking Strategy

Documents are chunked:

* by zoning section boundaries (`##`)
* with amendment metadata preserved
* with line-aware provenance tracking
* with cross-reference extraction

This preserves legal context and improves retrieval precision.

---

## Cross-Reference Gap Detection

The ingest pipeline detects:

* referenced zoning sections
* missing referenced sections in corpus

This allows the system to warn users when:

* corpus coverage is incomplete
* retrieved evidence may be insufficient

---

## Vintage and Historical Safeguards

The system identifies:

* historical zoning text
* superseded regulations
* ACS demographic vintages
* incomplete environmental designation datasets

Responses explicitly warn when retrieved information may be outdated or incomplete.

---

## Hybrid Structured + Prose Reasoning

The pipeline combines:

* structured parcel/site data
* zoning regulation retrieval
* legal reasoning using a local LLM

Questions are routed into:

* structured
* prose
* hybrid

retrieval modes.

---

# Architecture

```text
User Question
      ↓
Site Lookup (BBL)
      ↓
Question Routing
      ↓
Vector Retrieval (ChromaDB)
      ↓
Cross-Reference + Vintage Checks
      ↓
Prompt Assembly
      ↓
Local LLM (Ollama)
      ↓
Deterministic Citation Replacement
      ↓
Grounded Legal Response
```

---

# Tech Stack

## Retrieval

* ChromaDB
* SentenceTransformers (`all-MiniLM-L6-v2`)

## LLM

* Ollama
* Local inference pipeline

## Data

* NYC zoning markdown corpus
* PLUTO-style structured site records

## Evaluation

* Custom evaluation harness
* Provenance-aware scoring

---

# Repository Structure

```text
.
├── corpus/
│   └── zoning/
├── chroma_db/
├── logs/
├── notebooks/
├── src/
│   ├── llm/
│   ├── retrieval/
│   ├── routing/
│   ├── site/
│   ├── logging_utils/
│   ├── query.py
│   └── eval.py
├── README.md
├── requirements.txt
└── .env.example
```

---

# Setup

## 1. Clone Repository

```bash
git clone <repo_url>
cd intelli-site
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

### Windows

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Ollama

Install:
https://ollama.com

Pull model:

```bash
ollama pull llama3
```

---

## 5. Create `.env`

Example:

```env
CHROMA_PATH=chroma_db
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

---

# Ingest Pipeline

Run the notebook or ingest script to build the ChromaDB index.

The ingest stage:

* parses markdown zoning documents
* extracts metadata
* builds provenance-aware chunks
* creates cross-reference maps
* stores embeddings in ChromaDB

---

# Running Queries

Example:

```bash
python -m src.query \
--bbl 4049630075 \
--question "What are the rear yard requirements for this property?"
```

---

# Evaluation

Run the evaluation harness:

```bash
python -m src.eval
```

The evaluation pipeline tests:

* retrieval quality
* abstention behavior
* citation grounding
* historical/vintage handling
* cross-reference gaps

---

# Current Limitations

* Dense vector retrieval only (BM25 hybrid retrieval planned)
* Small zoning corpus
* Limited commercial district coverage
* No frontend/UI yet
* No reranking stage yet

---

# Planned Improvements

* Hybrid BM25 + vector retrieval
* Cross-encoder reranking
* Query expansion
* Applicability-aware retrieval
* Graph-based cross-reference traversal
* Frontend citation highlighting
* Structured provenance citations
* Automated benchmark suite

---

# Why This Project Matters

Legal and zoning workflows require:

* grounded answers
* traceable evidence
* abstention when evidence is insufficient
* awareness of historical amendments and missing references

This project explores how provenance-aware RAG systems can improve reliability and transparency in legal AI applications.

---

# Example Evaluation Snapshot

```text
PASS: 2/8
PARTIAL: 3/8
FAIL: 3/8
```

The current system already demonstrates:

* grounded citation generation
* legal abstention behavior
* cross-reference awareness
* provenance-aware retrieval

Further improvements are focused on retrieval quality and applicability reasoning.

---
