# reasoning.md — Intelli-Site Legal Zoning RAG

## Architecture

```
BBL + Question
      │
      ▼
 Site Lookup ──────────────────── site_records.csv + PLUTO
      │
      ▼
 LLM Router (llama3, temp=0) ──── classifies: structured | prose | hybrid
      │                            fallback: hybrid on any error
      ├── structured ──► site context only
      ├── prose      ──► ChromaDB retrieval only
      └── hybrid     ──► both
                          │
                          ▼
              Vintage + cross-ref check
                          │
                          ▼
                   Prompt builder ──── cite-or-abstain instruction
                          │
                          ▼
              Ollama · llama3 · generate
                          │
                          ▼
             Citation postprocessor ── [SOURCE_N] → [Section | file | lines]
                          │
                          ▼
              JSON output: response · chunks · scores · warnings
```

---

## Chunking strategy

**Decision:** section-level splits at `## ` headers. If a section exceeds ~2400 characters, split further at paragraph boundaries.

**Why:** Legal documents are rule systems, not prose. Each section is a self-contained regulatory unit with its own applicability scope. Splitting mid-section destroys the legal context a model needs to reason correctly. Fixed-size token windows were tested and rejected — they routinely cut applicability clauses from the rules they govern.

**Metadata stored per chunk:** `source_file`, `section_title`, `last_amended`, `start_line`, `end_line`, `has_cross_ref`. The amendment date is stored so vintage conflicts are detectable at retrieval time, not after.

**Cross-reference map:** at ingest, regex scans all chunks for `Section \d{2}-\d{2,3}` patterns. A `cross_ref_map.json` records which section IDs are present vs referenced-but-missing. Used at query time to surface corpus gaps explicitly.

---

## Retrieval design

| Parameter | Value | Reason |
|---|---|---|
| Model | `all-MiniLM-L6-v2` | Local, 90 MB, no API cost, adequate for regulatory English |
| Store | ChromaDB persistent | Metadata filtering on `section_title` is first-class |
| Similarity threshold | 0.38 | 0.55 cut correct zoning chunks scoring 0.45–0.52 on paraphrased queries |
| top-k | 5 | Enough for primary section + referenced dependencies |

**Keyword pre-filter:** before dense retrieval, if the question contains known trigger phrases (e.g. "air conditioning", "obstruction", "rear yard"), the retriever runs a metadata-filtered pass first to guarantee those section titles are included. Dense embedding alone missed "AC unit → permitted obstruction" because the terminology gap is too large for a 384-dim model.

**What was rejected:** BM25 alone (no semantic understanding), cross-encoder reranking (latency on 3060 not worth it for 10 documents), full-document embedding (too coarse, citation impossible).

---

## Routing logic

**Decision:** LLM-based router (llama3, `temperature=0`, `num_predict=5`). Returns one word: `structured`, `prose`, or `hybrid`. Any error or invalid output defaults to `hybrid`.

**Why LLM over keywords:** zoning questions are semantically ambiguous. "What is the FAR for this site?" looks factual but may require applicability reasoning over prose. A keyword router misclassified this as `structured` and suppressed retrieval entirely. The LLM router handles paraphrases and hybrid intent correctly.

**Why not always-hybrid:** chosen as a deliberate architecture decision rather than a safety net. The router adds ~1–2s latency but provides a cleaner separation between data sources that aids debugging and eval transparency.

---

## Failure handling

Two explicit failure modes:

**1. Retrieval score below threshold** — no chunks pass 0.38. The prompt receives an explicit message: `"No zoning documents matched above the relevance threshold."` The model is instructed to abstain with a specific explanation of what is missing, not a generic "I don't know."

**2. Cross-reference gap** — `cross_ref_map.json` flags referenced sections not in corpus. The prompt builder injects: `"Section 23-341 is referenced but not present in the corpus — do not speculate about its content."`

**What abstention looks like:** the answer contains `"The corpus does not support this question"` followed by what specifically is missing and where to look next (e.g. NYC DCP archive, OER for E designations).

Absence of retrieved evidence is not treated as proof a regulation does not exist — the prompt explicitly states this distinction.

---

## What I would build next

**Hybrid BM25 + dense retrieval.**

The single largest remaining failure mode is terminology mismatch — a user says "AC unit" and the corpus says "mechanical equipment obstruction." Dense embeddings at 384 dimensions bridge some of this gap but not reliably. BM25 catches exact legal terms (section numbers, district codes, defined terms like "permitted obstruction") that semantic search misses. Reciprocal rank fusion of both scores would improve retrieval recall without adding latency from a reranker. With only 10 documents this is straightforward to implement and would directly improve eval cases 2, 3, and 5.