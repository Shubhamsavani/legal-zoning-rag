import chromadb

from dotenv import load_dotenv

import os


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
# BUILD SECTION LOOKUP INDEX
# =====================================================

def build_section_lookup_index():

    """
    Build deterministic section lookup map.

    section_id -> chunk object
    """

    lookup = {}

    all_chunks = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    ids = all_chunks["ids"]

    documents = all_chunks["documents"]

    metadatas = all_chunks["metadatas"]

    for idx in range(len(ids)):

        chunk_id = ids[idx]

        document = documents[idx]

        metadata = metadatas[idx]

        section_id = metadata.get(
            "section_id"
        )

        if not section_id:
            continue

        lookup[section_id] = {

            "chunk_id":
            chunk_id,

            "document":
            document,

            "metadata":
            metadata
        }

    return lookup


# =====================================================
# GLOBAL LOOKUP
# =====================================================

SECTION_LOOKUP = (
    build_section_lookup_index()
)


# =====================================================
# DEPENDENCY EXPANSION
# =====================================================

def expand_chunk_dependencies(

    retrieved_chunks: list,

    existing_chunk_ids: set,

    build_chunk_object_fn
):

    expanded_chunks = []

    # =================================================
    # PROCESS SEMANTIC CHUNKS
    # =================================================

    for chunk in retrieved_chunks:

        cross_refs = chunk.get(
            "cross_refs",
            "NONE"
        )

        if cross_refs == "NONE":
            continue

        referenced_sections = (
            cross_refs.split("|")
        )

        # =============================================
        # ONE HOP EXPANSION
        # =============================================

        for section_id in referenced_sections:

            dependency_match = (
                SECTION_LOOKUP.get(
                    section_id
                )
            )

            if not dependency_match:
                continue

            dependency_chunk_id = (
                dependency_match["chunk_id"]
            )

            # =========================================
            # DEDUPLICATION
            # =========================================

            if (
                dependency_chunk_id
                in
                existing_chunk_ids
            ):
                continue

            existing_chunk_ids.add(
                dependency_chunk_id
            )

            citation_id = (
                f"SOURCE_"
                f"{len(retrieved_chunks) + len(expanded_chunks) + 1}"
            )

            expanded_chunks.append(

                build_chunk_object_fn(

                    citation_id=
                    citation_id,

                    chunk_id=
                    dependency_chunk_id,

                    document=
                    dependency_match["document"],

                    metadata=
                    dependency_match["metadata"],

                    distance=
                    "DEPENDENCY",

                    retrieval_type=
                    "dependency"
                )
            )

    return expanded_chunks


# =====================================================
# TEST BLOCK
# =====================================================

if __name__ == "__main__":

    print("\nDEPENDENCY GRAPH LOADED\n")

    print(
        f"TOTAL SECTIONS: "
        f"{len(SECTION_LOOKUP)}"
    )

    print("\nEXAMPLE SECTION IDS:\n")

    example_keys = list(
        SECTION_LOOKUP.keys()
    )[:10]

    for key in example_keys:

        print(key)
