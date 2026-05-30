# Intelli-Site — Legal Zoning RAG

Provenance-aware RAG system for NYC zoning analysis. Takes a BBL and a natural language question, returns a grounded answer with citations, retrieval scores, and vintage warnings.

---

## Stack

| Component | Choice |
|---|---|
| LLM | llama3 via Ollama |
| Embeddings | all-MiniLM-L6-v2 |
| Vector store | ChromaDB (local persistent) |
| Structured data | pandas (site_records.csv + PLUTO) |
| UI | Streamlit |

---

## Install

```bash
git clone https://github.com/Shubhamsavani/legal-zoning-rag
cd legal-zoning-rag
pip install -r requirements.txt
```

Pull the LLM:

```bash
ollama pull llama3
ollama serve
```

---

## Environment variables

Create `.env` in the project root:

```env
CHROMA_PATH=chroma_db
COLLECTION_NAME=zoning_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
RETRIEVAL_THRESHOLD=0.38
TOP_K=5
CORPUS_DIR=corpus/zoning
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## Run — ingest first

Build the ChromaDB index from the zoning corpus (run once):

```bash
jupyter nbconvert --to notebook --execute notebooks/ingest_pipeline.ipynb
```

This produces `chroma_db/` and `chroma_db/cross_ref_map.json`.

---

## Run — CLI

```bash
python -m src.query \
  --bbl 4049630075 \
  --question "Does this site have an E designation and what does that mean?"
```

Optional flags:

```bash
--top-k 5          # chunks to retrieve (default: 5)
--threshold 0.38   # similarity cutoff (default: 0.38)
--no-log           # skip writing log file
--verbose          # print pipeline steps
```

---

## Run — Streamlit UI

```bash
streamlit run app.py
```

The UI renders answers with clickable citation pills. Clicking a citation opens the source markdown file with the cited lines highlighted.

---

## Run — evaluation

```bash
python -m src.eval_
```

With LLM judge disabled (faster):

```bash
python -m src.eval_ --no-judge
```

Single case debug:

```bash
python -m src.eval_ --case 4
```

Results written to `logs/eval_results.json`.

---

## Retrieval transparency

Every query returns and logs:

```json
{
  "bbl": "4049630075",
  "question": "...",
  "route": "hybrid",
  "retrieved_chunks": [
    {
      "citation_id": "SOURCE_1",
      "source_file": "zr_09_ceqr_e_designations.md",
      "section_title": "What is an (E) Designation?",
      "start_line": 14,
      "end_line": 28,
      "distance": 0.248
    }
  ],
  "warnings": ["(E) corpus data is from Feb 2018 — verify with NYC OER"],
  "response": "..."
}
```

---

## Project structure

```
corpus/
  zoning/          ← 10 NYC Zoning Resolution excerpts (.md)
  structured/      ← site_records.csv, pluto_25v4.csv

src/
  routing/         ← router.py (LLM-based, llama3)
  retrieval/       ← retriever.py, vintage_checks.py, citation_postprocessor.py
  llm/             ← ollama_client.py, prompt_builder.py
  site/            ← lookup.py, formatter.py
  logging_utils/   ← logger.py
  query.py         ← main pipeline entrypoint (run_query_pipeline)
  eval_.py         ← 3-layer evaluation (deterministic + heuristic + LLM judge)

notebooks/
  ingest_pipeline.ipynb   ← chunking + embedding + ChromaDB build

app.py             ← Streamlit UI
reasoning.md       ← design decisions
requirements.txt
.env.example
```

---

## Known limitations

- Applicability reasoning across zoning districts is imperfect when relevant rules span multiple sections
- Historical/vintage questions require the corpus to contain multiple amendment snapshots — it does not
- Retrieval quality is sensitive to chunking strategy; subsection-level splits were tested and rejected (fragmented legal context)
- llama3 at Q4 quantization introduces occasional hallucination under weak retrieval — the prompt enforces explicit abstention to mitigate this

---

# Future Improvements

The single most important future improvement would be:

* Experimenting with chunking strategies

Different legal chunking approaches produced significantly different retrieval behavior and grounding quality during experimentation.

---

# Notes

A second experimental evaluation pipeline using LLM-based judging/prompts was explored, but deterministic behavioral evaluation was ultimately preferred for transparency and reproducibility.
