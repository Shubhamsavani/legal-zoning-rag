import chromadb

from sentence_transformers import (
    SentenceTransformer
)

from dotenv import load_dotenv

import os

from typing import Union


from src.retrieval.dependency_graph import (
    expand_chunk_dependencies
)



# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "chroma_legal_db"
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "nyc_zoning_resolution"
)

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

MAX_CHARS = 1200


# =====================================================
# LOAD EMBEDDING MODEL
# =====================================================

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)


# =====================================================
# CHROMA CLIENT
# =====================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# =====================================================
# BUILD CHUNK OBJECT
# =====================================================

def build_chunk_object(

    citation_id: str,

    chunk_id: str,

    document: str,

    metadata: dict,

    distance: Union[float, str],

    retrieval_type: str
):

    document = document[:MAX_CHARS]

    return {

        # =============================================
        # RETRIEVAL
        # =============================================

        "citation_id":
        citation_id,

        "retrieval_type":
        retrieval_type,

        "distance":
        distance,

        # =============================================
        # IDENTIFIERS
        # =============================================

        "chunk_id":
        chunk_id,

        "section_id":
        metadata.get(
            "section_id"
        ),

        # =============================================
        # CONTENT
        # =============================================

        "text":
        document,

        # =============================================
        # PROVENANCE
        # =============================================

        "source_file":
        metadata.get(
            "source_file"
        ),

        "section_title":
        metadata.get(
            "section_title"
        ),

        "parent_section_id":
        metadata.get(
            "parent_section_id"
        ),

        "last_amended":
        metadata.get(
            "last_amended"
        ),

        # =============================================
        # LEGAL METADATA
        # =============================================

        "district_scope":
        metadata.get(
            "district_scope"
        ),

        "is_historical":
        metadata.get(
            "is_historical"
        ),

        # =============================================
        # LEGAL DEPENDENCIES
        # =============================================

        "cross_refs":
        metadata.get(
            "cross_refs",
            "NONE"
        ),

        "article_refs":
        metadata.get(
            "article_refs",
            "NONE"
        ),

        "appendix_refs":
        metadata.get(
            "appendix_refs",
            "NONE"
        )
    }


# =====================================================
# MAIN RETRIEVAL FUNCTION
# =====================================================

def retrieve_chunks(

    question: str,

    top_k: int = 5,

    threshold: float = 0.80
):

    # =================================================
    # GENERATE QUERY EMBEDDING
    # =================================================

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    # =================================================
    # CHROMA QUERY
    # =================================================

    results = collection.query(

        query_embeddings=[query_embedding],

        n_results=top_k
    )

    retrieved_chunks = []

    existing_chunk_ids = set()

    documents = results[
        "documents"
    ][0]

    metadatas = results[
        "metadatas"
    ][0]

    distances = results[
        "distances"
    ][0]

    ids = results[
        "ids"
    ][0]

    # =================================================
    # PRIMARY SEMANTIC RETRIEVAL
    # =================================================

    for idx in range(len(documents)):

        distance = distances[idx]

        # =============================================
        # DISTANCE FILTERING
        # =============================================
        # print(
        #     f"DEBUG DISTANCE: "
        #     f"{distance}"
        # )


        if distance > threshold:
            continue

        document = documents[idx]

        metadata = metadatas[idx]

        chunk_id = ids[idx]

        # =============================================
        # DEDUPLICATION
        # =============================================

        if chunk_id in existing_chunk_ids:
            continue

        existing_chunk_ids.add(
            chunk_id
        )

        citation_id = (
            f"SOURCE_{len(retrieved_chunks)+1}"
        )

        retrieved_chunks.append(

            build_chunk_object(

                citation_id=
                citation_id,

                chunk_id=
                chunk_id,

                document=
                document,

                metadata=
                metadata,

                distance=
                distance,

                retrieval_type=
                "semantic"
            )
        )

    # =================================================
    # ONE HOP DEPENDENCY EXPANSION
    # =================================================


    dependency_chunks = (

        expand_chunk_dependencies(

            retrieved_chunks=
            retrieved_chunks,

            existing_chunk_ids=
            existing_chunk_ids,

            build_chunk_object_fn=
            build_chunk_object
        )
    )


    retrieved_chunks.extend(
        dependency_chunks
    )

    # =================================================
    # SORT FINAL RESULTS
    # =================================================

    def sort_key(chunk):

        if chunk["distance"] == "DEPENDENCY":
            return 9999

        return chunk["distance"]

    retrieved_chunks = sorted(

        retrieved_chunks,

        key=sort_key
    )


    for i, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        chunk["citation_id"] = (
            f"SOURCE_{i}"
        )



    return retrieved_chunks


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    question = (
        "What are rear yard "
        "requirements?"
    )

    chunks = retrieve_chunks(
        question=question
    )

    print("\n=== RETRIEVED CHUNKS ===\n")

    for chunk in chunks:

        print(
            f"{chunk['citation_id']}"
        )

        print(
            f"Retrieval Type: "
            f"{chunk['retrieval_type']}"
        )

        print(
            f"Source: "
            f"{chunk['source_file']}"
        )

        print(
            f"Section ID: "
            f"{chunk['section_id']}"
        )

        print(
            f"Section Title: "
            f"{chunk['section_title']}"
        )

        print(
            f"Distance: "
            f"{chunk['distance']}"
        )

        print(
            f"Cross Refs: "
            f"{chunk['cross_refs']}"
        )

        print(
            f"Historical: "
            f"{chunk['is_historical']}"
        )

        print(
            chunk["text"][:300]
        )

        print("\n" + "="*60 + "\n")
