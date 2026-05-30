import streamlit as st

from src.query import (
    run_query_pipeline
)

from src.ui.source_viewer import (
    load_source_file,
    build_highlighted_markdown
)


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title="Intelli-Site",

    page_icon="🏙️",

    layout="wide"
)


# =====================================================
# HEADER
# =====================================================

st.title(
    "🏙️ Intelli-Site"
)

st.subheader(
    "Provenance-Aware Legal RAG "
    "for NYC Zoning Analysis"
)

st.markdown("---")


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header(
    "Query Settings"
)

top_k = st.sidebar.slider(

    "Top-K Retrieval",

    min_value=1,

    max_value=10,

    value=5
)

threshold = st.sidebar.slider(

    "Similarity Threshold",

    min_value=0.0,

    max_value=1.0,

    value=0.55
)

show_prompt = st.sidebar.checkbox(
    "Show Prompt"
)

show_chunks = st.sidebar.checkbox(

    "Show Retrieved Chunks",

    value=True
)


# =====================================================
# INPUTS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    bbl = st.text_input(

        "BBL",

        value="4049630075"
    )

with col2:

    question = st.text_input(

        "Question",

        value=(
            "What are the rear yard "
            "requirements for this property?"
        )
    )


# =====================================================
# RUN QUERY
# =====================================================

if st.button(
    "Run Intelli-Site Query"
):

    with st.spinner(
        "Running legal RAG pipeline..."
    ):

        result = run_query_pipeline(

            bbl=bbl,

            question=question,

            top_k=top_k,

            threshold=threshold,

            save_logs=False,

            verbose=False
        )

    # =================================================
    # MAIN RESPONSE
    # =================================================

    st.markdown("---")

    st.header(
        "📌 Final Response"
    )

    st.write(
        result["response"]
    )

    # =================================================
    # ROUTE + WARNINGS
    # =================================================

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Route")

        st.code(
            result["route"]
        )

    with col2:

        st.subheader(
            "Warnings"
        )

        if result["warnings"]:

            for warning in result["warnings"]:

                st.warning(warning)

        else:

            st.success(
                "No warnings"
            )

    # =================================================
    # SITE CONTEXT
    # =================================================

    st.markdown("---")

    st.header(
        "🏢 Site Context"
    )

    st.text(
        result["site_context"]
    )

    # =================================================
    # RETRIEVED CHUNKS
    # =================================================

    if show_chunks:

        st.markdown("---")

        st.header(
            "📚 Retrieved Chunks"
        )

        for idx, chunk in enumerate(

            result["retrieved_chunks"]
        ):

            citation_label = (

                f"{chunk['citation_id']} | "
                f"{chunk['section_title']}"
            )

            with st.expander(
                citation_label
            ):

                # =====================================
                # CITATION METADATA
                # =====================================

                st.markdown(
                    f"""
### Citation Metadata

**Source File:**  
{chunk['source_file']}

**Lines:**  
{chunk['start_line']}-{chunk['end_line']}

**Distance:**  
{chunk['distance']:.4f}
"""
                )

                # =====================================
                # RETRIEVED CHUNK
                # =====================================

                st.subheader(
                    "Retrieved Chunk"
                )

                st.code(
                    chunk["text"]
                )

                # =====================================
                # SOURCE FILE VIEWER
                # =====================================

                if st.button(

                    f"Open Source File "
                    f"({chunk['citation_id']})",

                    key=f"open_{idx}"
                ):

                    lines = load_source_file(

                        chunk["source_file"]
                    )

                    if lines is None:

                        st.error(
                            "Source file not found."
                        )

                    else:

                        highlighted = (

                            build_highlighted_markdown(

                                lines=lines,

                                start_line=chunk[
                                    "start_line"
                                ],

                                end_line=chunk[
                                    "end_line"
                                ]
                            )
                        )

                        st.markdown("---")

                        st.subheader(
                            f"📄 "
                            f"{chunk['source_file']}"
                        )

                        st.markdown(
                            highlighted
                        )

    # =================================================
    # PROMPT
    # =================================================

    if show_prompt:

        st.markdown("---")

        st.header(
            "🧠 Final Prompt"
        )

        st.code(
            result["prompt"]
        )