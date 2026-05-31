"""
src/retrieval/retriever.py

Hybrid legal retrieval:
- Dense retrieval (ChromaDB)
- Sparse retrieval (BM25)
- Reciprocal Rank Fusion (RRF)
- Similarity threshold filtering
- Dependency graph expansion

Designed for:
Intelli-Site — provenance-aware legal RAG for NYC zoning analysis.
"""

import json
import pickle
import re
import os

from pathlib import Path

import chromadb

from dotenv import load_dotenv

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

# ─────────────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────────────

load_dotenv()

# ─────────────────────────────────────────────────────
# ENVIRONMENT CONFIG
# ─────────────────────────────────────────────────────

PROJECT_ROOT = Path(
    os.getenv("PROJECT_ROOT")
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH"
)

COLLECTION = os.getenv(
    "COLLECTION_NAME",
    "zoning_docs"
)

EMBED_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

BM25_PATH = (
    PROJECT_ROOT
    / "chroma_db"
    / "bm25_index.pkl"
)

GRAPH_PATH = (
    PROJECT_ROOT
    / "chroma_db"
    / "section_graph.json"
)

DEFAULT_TOP_K = 5

DEFAULT_THRESHOLD = 0.38

MAX_DEPENDENCIES = 3

RRF_K = 60

# ─────────────────────────────────────────────────────
# LAZY SINGLETONS
# ─────────────────────────────────────────────────────

_collection = None

_bm25 = None

_bm25_ids = None

_graph = None

# ─────────────────────────────────────────────────────
# LOAD CHROMADB
# ─────────────────────────────────────────────────────

def _get_collection():

    global _collection

    if _collection is None:

        print(
            f"[INFO] Connecting to ChromaDB:\n"
            f"{CHROMA_PATH}\n"
        )

        ef = SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )

        client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        print(
            "[INFO] Available collections:"
        )

        print(client.list_collections())

        _collection = client.get_collection(
            COLLECTION,
            embedding_function=ef
        )

        print(
            f"[INFO] Loaded collection: "
            f"{COLLECTION}"
        )

    return _collection

# ─────────────────────────────────────────────────────
# LOAD BM25
# ─────────────────────────────────────────────────────

def _get_bm25():

    global _bm25
    global _bm25_ids

    if _bm25 is None:

        if not BM25_PATH.exists():

            raise FileNotFoundError(
                f"BM25 index not found at:\n"
                f"{BM25_PATH}\n\n"
                f"Run notebooks/02_dual_index.ipynb first."
            )

        print(
            f"[INFO] Loading BM25 index from:\n"
            f"{BM25_PATH}\n"
        )

        with open(BM25_PATH, "rb") as f:

            payload = pickle.load(f)

        _bm25 = payload["bm25"]

        _bm25_ids = payload["corpus_ids"]

        print(
            f"[INFO] Loaded BM25 corpus "
            f"with {len(_bm25_ids)} chunks"
        )

    return _bm25, _bm25_ids

# ─────────────────────────────────────────────────────
# LOAD GRAPH
# ─────────────────────────────────────────────────────

def _get_graph():

    global _graph

    if _graph is None:

        if not GRAPH_PATH.exists():

            print(
                "[WARNING] Graph file not found."
            )

            _graph = {"nodes": {}}

        else:

            print(
                f"[INFO] Loading graph from:\n"
                f"{GRAPH_PATH}\n"
            )

            _graph = json.loads(
                GRAPH_PATH.read_text(
                    encoding="utf-8"
                )
            )

            print(
                f"[INFO] Loaded "
                f"{len(_graph['nodes'])} "
                f"graph nodes"
            )

    return _graph

# ─────────────────────────────────────────────────────
# LEGAL TOKENIZER
# ─────────────────────────────────────────────────────

def _tokenize(text: str) -> list:

    return re.findall(
        r'[a-z0-9\-\(\)]+',
        text.lower()
    )

# ─────────────────────────────────────────────────────
# STEP 1 — DENSE RETRIEVAL
# ─────────────────────────────────────────────────────

def _dense_retrieve(
    question: str,
    top_k: int
) -> list:

    col = _get_collection()

    raw = col.query(

        query_texts=[question],

        n_results=top_k,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    results = []

    for cid, doc, meta, dist in zip(

        raw["ids"][0],

        raw["documents"][0],

        raw["metadatas"][0],

        raw["distances"][0]
    ):

        results.append({

            "chunk_id": cid,

            "source_file": meta.get(
                "source_file", ""
            ),

            "section_title": meta.get(
                "section_title", ""
            ),

            "subsection_title": meta.get(
                "subsection_title", ""
            ),

            "section_id": meta.get(
                "section_id", ""
            ),

            "node_id": meta.get(
                "node_id", ""
            ),

            "last_amended": meta.get(
                "last_amended", ""
            ),

            "start_line": meta.get(
                "start_line", 0
            ),

            "end_line": meta.get(
                "end_line", 0
            ),

            "has_cross_ref": meta.get(
                "has_cross_ref", False
            ),

            "references": json.loads(
                meta.get("references", "[]")
            ),

            "distance": round(dist, 4),

            "similarity": round(
                1 - dist,
                4
            ),

            "bm25_score": None,

            "text": doc,

            "retrieval_method": "dense"
        })

    return results

# ─────────────────────────────────────────────────────
# STEP 2 — BM25 RETRIEVAL
# ─────────────────────────────────────────────────────

def _bm25_retrieve(
    question: str,
    top_k: int
) -> list:

    bm25, corpus_ids = _get_bm25()

    col = _get_collection()

    tokens = _tokenize(question)

    scores = bm25.get_scores(tokens)

    top_indices = sorted(

        range(len(scores)),

        key=lambda i: scores[i],

        reverse=True

    )[:top_k]

    results = []

    for idx in top_indices:

        if scores[idx] <= 0:
            continue

        chunk_id = corpus_ids[idx]

        raw = col.get(

            ids=[chunk_id],

            include=[
                "documents",
                "metadatas"
            ]
        )

        if not raw["documents"]:
            continue

        doc = raw["documents"][0]

        meta = raw["metadatas"][0]

        results.append({

            "chunk_id": chunk_id,

            "source_file": meta.get(
                "source_file", ""
            ),

            "section_title": meta.get(
                "section_title", ""
            ),

            "subsection_title": meta.get(
                "subsection_title", ""
            ),

            "section_id": meta.get(
                "section_id", ""
            ),

            "node_id": meta.get(
                "node_id", ""
            ),

            "last_amended": meta.get(
                "last_amended", ""
            ),

            "start_line": meta.get(
                "start_line", 0
            ),

            "end_line": meta.get(
                "end_line", 0
            ),

            "has_cross_ref": meta.get(
                "has_cross_ref", False
            ),

            "references": json.loads(
                meta.get("references", "[]")
            ),

            "distance": None,

            "similarity": None,

            "bm25_score": round(
                float(scores[idx]),
                4
            ),

            "text": doc,

            "retrieval_method": "bm25"
        })

    return results

# ─────────────────────────────────────────────────────
# STEP 3 — RRF MERGE
# ─────────────────────────────────────────────────────

def _rrf_merge(
    dense: list,
    bm25: list,
    top_k: int
) -> list:

    rrf_scores = {}

    chunk_store = {}

    for rank, chunk in enumerate(dense):

        cid = chunk["chunk_id"]

        rrf_scores[cid] = (
            rrf_scores.get(cid, 0)
            + 1 / (RRF_K + rank + 1)
        )

        chunk_store[cid] = chunk

    for rank, chunk in enumerate(bm25):

        cid = chunk["chunk_id"]

        rrf_scores[cid] = (
            rrf_scores.get(cid, 0)
            + 1 / (RRF_K + rank + 1)
        )

        if cid not in chunk_store:

            chunk_store[cid] = chunk

        else:

            chunk_store[cid][
                "retrieval_method"
            ] = "dense+bm25"

            chunk_store[cid][
                "bm25_score"
            ] = chunk.get("bm25_score")

    merged = sorted(

        rrf_scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    results = []

    for cid, score in merged[:top_k]:

        c = chunk_store[cid].copy()

        c["rrf_score"] = round(
            score,
            6
        )

        results.append(c)

    return results

# ─────────────────────────────────────────────────────
# STEP 4 — THRESHOLD FILTER
# ─────────────────────────────────────────────────────

def _apply_threshold(
    chunks: list,
    threshold: float
) -> list:

    kept = []

    for c in chunks:

        sim = c.get("similarity")

        if sim is None:

            kept.append(c)

        elif (
            sim >= threshold
            or c.get("retrieval_method")
            == "dense+bm25"
        ):

            kept.append(c)

    return kept

# ─────────────────────────────────────────────────────
# STEP 5 — DEPENDENCY EXPANSION
# ─────────────────────────────────────────────────────

def _expand_dependencies(
    chunks: list,
    max_deps: int = MAX_DEPENDENCIES
):

    graph = _get_graph()

    nodes = graph.get(
        "nodes",
        {}
    )

    col = _get_collection()

    seen_ids = {
        c["chunk_id"]
        for c in chunks
    }

    expanded = list(chunks)

    warnings = []

    dep_count = 0

    priority_chunks = sorted(

        chunks,

        key=lambda c: (

            c.get("retrieval_method")
            == "dense+bm25",

            c.get("has_cross_ref", False)

        ),

        reverse=True
    )

    for chunk in priority_chunks:

        if dep_count >= max_deps:
            break

        node_id = chunk.get(
            "node_id",
            ""
        )

        node = nodes.get(
            node_id,
            {}
        )

        refs = node.get(
            "references",
            []
        )

        for ref_id in refs:

            if dep_count >= max_deps:
                break

            if ref_id not in nodes:

                warnings.append(

                    f"Section {ref_id} "
                    f"referenced by {node_id} "
                    f"is not in corpus."

                )

                continue

            dep_node = nodes[ref_id]

            dep_chunk_id = (
                f"{dep_node['source_file']}::{ref_id}"
            )

            if dep_chunk_id in seen_ids:
                continue

            raw = col.get(

                ids=[dep_chunk_id],

                include=[
                    "documents",
                    "metadatas"
                ]
            )

            if not raw["documents"]:
                continue

            doc = raw["documents"][0]

            meta = raw["metadatas"][0]

            expanded.append({

                "chunk_id": dep_chunk_id,

                "source_file": meta.get(
                    "source_file", ""
                ),

                "section_title": meta.get(
                    "section_title", ""
                ),

                "subsection_title": meta.get(
                    "subsection_title", ""
                ),

                "section_id": meta.get(
                    "section_id", ""
                ),

                "node_id": ref_id,

                "last_amended": meta.get(
                    "last_amended", ""
                ),

                "start_line": meta.get(
                    "start_line", 0
                ),

                "end_line": meta.get(
                    "end_line", 0
                ),

                "has_cross_ref": meta.get(
                    "has_cross_ref", False
                ),

                "references": json.loads(
                    meta.get("references", "[]")
                ),

                "distance": None,

                "similarity": None,

                "bm25_score": None,

                "text": doc,

                "retrieval_method": "dependency",

                "dependency_of": node_id
            })

            seen_ids.add(dep_chunk_id)

            dep_count += 1

    return expanded, warnings

# ─────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────

def retrieve_chunks(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD
):

    dense = _dense_retrieve(
        question,
        top_k
    )

    sparse = _bm25_retrieve(
        question,
        top_k
    )

    merged = _rrf_merge(
        dense,
        sparse,
        top_k
    )

    kept = _apply_threshold(
        merged,
        threshold
    )

    final, warnings = _expand_dependencies(
        kept
    )

    for i, chunk in enumerate(final):

        chunk["citation_id"] = (
            f"SOURCE_{i + 1}"
        )

    return final, warnings
