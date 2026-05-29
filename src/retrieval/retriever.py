import chromadb

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)


CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "zoning_docs"


embedding_function = (
    SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)


def retrieve_chunks(
    question: str,
    top_k: int = 5,
    threshold: float = 0.55
) -> list:

    results = collection.query(

        query_texts=[question],

        n_results=top_k
    )

    retrieved_chunks = []

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        similarity = 1 - distance

        if similarity < threshold:
            continue

        retrieved_chunks.append({

            "text": document,

            "source_file": metadata.get(
                "source_file"
            ),

            "section_title": metadata.get(
                "section_title"
            ),

            "last_amended": metadata.get(
                "last_amended"
            ),

            "similarity": round(
                similarity,
                4
            ),

            "has_cross_ref": metadata.get(
                "has_cross_ref",
                False
            )
        })

    return retrieved_chunks

# # test
# if __name__ == "__main__":

#     results = retrieve_chunks(

#         question="What are rear yard requirements in R6 districts?",

#         top_k=5,

#         threshold=0.30
#     )

#     for idx, chunk in enumerate(results, start=1):

#         print("\n" + "=" * 80)

#         print(f"RESULT {idx}")

#         print(f"Similarity: {chunk['similarity']}")

#         print(f"Source: {chunk['source_file']}")

#         print(f"Section: {chunk['section_title']}")

#         print("\nTEXT:\n")

#         print(chunk["text"][:1000])