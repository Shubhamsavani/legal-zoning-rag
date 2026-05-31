"""
app.py

Run from project root:

streamlit run app.py
"""

import streamlit as st

from src.main import run_intelli_site


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

    value=0.38,

    step=0.01
)

show_chunks = st.sidebar.checkbox(

    "Show Retrieved Chunks",

    value=True
)

show_prompt = st.sidebar.checkbox(

    "Show Final Prompt",

    value=False
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
            "Can HVAC equipment "
            "project into a "
            "required rear yard?"
        )
    )


# =====================================================
# RUN BUTTON
# =====================================================

run_query = st.button(

    "Run Intelli-Site Query",

    type="primary",

    use_container_width=True
)


# =====================================================
# PIPELINE EXECUTION
# =====================================================

if run_query:

    with st.spinner(

        "Running Intelli-Site pipeline..."
    ):

        result = run_intelli_site(

            question=question,

            bbl=bbl,

            top_k=top_k,

            threshold=threshold
        )

    # =================================================
    # FINAL ANSWER
    # =================================================

    st.markdown("---")

    st.header(
        "📌 Final Answer"
    )

    st.markdown(

        f"""
<div style="
padding:18px;
border-radius:12px;
background-color:#111827;
color:white;
font-size:16px;
line-height:1.7;
">
{result['formatted_response']}
</div>
""",

        unsafe_allow_html=True
    )

    # =================================================
    # ROUTING
    # =================================================

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🧭 Route")

        st.code(
            result["route"]
        )

    with col2:

        st.subheader(
            "📅 Query Year"
        )

        st.code(
            str(
                result.get(
                    "query_year"
                )
            )
        )

    # =================================================
    # WARNINGS
    # =================================================

    if result["warnings"]:

        st.markdown("---")

        st.header(
            "⚠️ Warnings"
        )

        for warning in result["warnings"]:

            st.warning(
                warning
            )

    # =================================================
    # SITE SUMMARY
    # =================================================

    if result["site_summary"]:

        st.markdown("---")

        st.header(
            "🏢 Site Summary"
        )

        st.json(
            result["site_summary"]
        )

    # =================================================
    # RETRIEVED CHUNKS
    # =================================================

    if (

        show_chunks

        and result["retrieved_chunks"]
    ):

        st.markdown("---")

        st.header(
            "📚 Retrieved Chunks"
        )

        for idx, chunk in enumerate(

            result["retrieved_chunks"]
        ):

            title = (

                f"{chunk['citation_id']} | "

                f"{chunk['subsection_title']}"
            )

            with st.expander(title):

                st.markdown(

                    f"""
### Citation Metadata

**Source File:**  
{chunk['source_file']}

**Section ID:**  
{chunk['section_id']}

**Node ID:**  
{chunk['node_id']}

**Retrieval Method:**  
{chunk['retrieval_method']}

**Lines:**  
{chunk['start_line']} - {chunk['end_line']}
"""
                )

                if chunk.get("similarity"):

                    st.markdown(

                        f"""
**Similarity Score:**  
{chunk['similarity']}
"""
                    )

                if chunk.get("bm25_score"):

                    st.markdown(

                        f"""
**BM25 Score:**  
{chunk['bm25_score']}
"""
                    )

                st.subheader(
                    "Chunk Text"
                )

                st.code(
                    chunk["text"]
                )

    # =================================================
    # CITATIONS USED
    # =================================================

    if result["retrieved_chunks"]:

        st.markdown("---")

        st.header(
            "📖 Citations Used"
        )

        seen = set()

        for chunk in result["retrieved_chunks"]:

            cid = chunk["citation_id"]

            if cid in seen:
                continue

            seen.add(cid)

            st.markdown(

                f"""
### [{cid}]

**Title:**  
{chunk['subsection_title']}

**Source File:**  
`{chunk['source_file']}`

**Lines:**  
{chunk['start_line']} - {chunk['end_line']}
"""
            )

    # =================================================
    # VALIDATION
    # =================================================

    st.markdown("---")

    st.header(
        "✅ Validation"
    )

    st.json(
        result["validation"]
    )

    # =================================================
    # FINAL PROMPT
    # =================================================

    if show_prompt:

        st.markdown("---")

        st.header(
            "🧠 Final Prompt"
        )

        st.code(
            result["prompt"]
        )