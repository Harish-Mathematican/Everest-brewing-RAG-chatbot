"""
#Gyan Labs - Enterprise RAG Platform & AI Intelligence Dashboard
================================================================
Interactive Streamlit interface offering multi-source RAG chat, live URL scraping,
document upload, natural language SQL analytics with Plotly charts, and vector space inspector.

DISCLAIMER:
Developed exclusively for educational, research, and open-source demonstration.
"""

import streamlit as st
import time
import os
import sys
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import EnterpriseRAGPipeline
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS

# Page Setup
st.set_page_config(
    page_title="#Gyan Labs — Enterprise RAG Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .badge-route {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #e0f2fe;
        color: #0369a1;
        margin-right: 8px;
    }
    .citation-card {
        background-color: #f8fafc;
        border-left: 3px solid #0284c7;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.88rem;
    }
    .prompt-chip {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 0.82rem;
        margin: 2px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_rag_pipeline():
    return EnterpriseRAGPipeline()


pipeline = get_rag_pipeline()

# Sidebar Controls & Stats
with st.sidebar:
    st.image("https://img.shields.io/badge/%23Gyan_Labs-Enterprise_RAG-0ea5e9?style=for-the-badge", use_container_width=True)
    st.markdown("### ⚙️ System Controls")

    retrieval_mode = st.selectbox(
        "Retrieval Search Algorithm",
        ["Maximal Marginal Relevance (MMR)", "Cosine Similarity (Standard)"],
        index=0
    )

    top_k = st.slider("Top-K Retrieved Context Chunks", min_value=1, max_value=8, value=4)
    force_route = st.selectbox("Intent Routing Override", ["Auto-Detect (Semantic)", "Knowledge Retrieval", "Structured SQL", "Fast FAQ", "Small-talk"])

    st.markdown("---")
    st.markdown("### 📊 Vector Store Telemetry")
    stats = pipeline.get_system_stats()
    st.metric("Total Indexed Chunks", stats["total_vectors"])
    st.metric("Active Data Sources", len(stats["indexed_sources"]))

    with st.expander("📚 View Indexed Sources"):
        for src in stats["indexed_sources"]:
            st.markdown(f"• `{src}`")

    if st.button("🔄 Re-Index All Enterprise Docs"):
        from src.config import DOCS_DIR
        pipeline.vector_store.reset()
        pipeline.ingest_directory(str(DOCS_DIR))
        st.success("Re-indexed all enterprise documentation successfully!")
        st.rerun()

    st.markdown("---")
    st.markdown("<small>Developed by **Harish Dhakal** &bull; #Gyan Labs</small>", unsafe_allow_html=True)

# Main Navigation Tabs
tab_chat, tab_ingest, tab_sql, tab_inspector, tab_architecture = st.tabs([
    "💬 RAG AI Assistant",
    "🌐 Multi-Source Ingestion",
    "📊 Text-to-SQL Analytics",
    "🔍 Vector Space Inspector",
    "🏛️ System Architecture"
])

# =====================================================================
# TAB 1: RAG AI CHATBOT
# =====================================================================
with tab_chat:
    st.markdown('<div class="main-header">⚡ #Gyan Labs Enterprise RAG Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-source semantic retrieval, structured SQL routing, and grounded source attribution.</div>', unsafe_allow_html=True)

    # Quick prompt suggestions
    st.markdown("**💡 Quick Prompt Suggestions:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    sample_to_run = None
    if q_col1.button("🤖 Agentic AI Architecture"):
        sample_to_run = "Explain the multi-agent orchestration architecture at Gyan Labs"
    if q_col2.button("🛡️ Zero-Trust Security"):
        sample_to_run = "What is our zero-trust security and SOC 2 governance framework?"
    if q_col3.button("📊 List GPU Clusters (SQL)"):
        sample_to_run = "List all GPU compute nodes and their hourly costs"
    if q_col4.button("🔍 MMR Vector Search"):
        sample_to_run = "How does hybrid vector retrieval with MMR re-ranking work?"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am the **#Gyan Labs Knowledge Intelligence Assistant**. Ask me anything about our Agentic AI architectures, GPU infrastructure, zero-trust security policies, or enterprise SQL analytics!",
                "sources": [],
                "route": "small_talk",
                "latency": 0.01,
                "confidence": 1.0
            }
        ]

    # Render chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("route"):
                route_icons = {
                    "knowledge_retrieval": "🎯 Knowledge Retrieval",
                    "structured_sql": "📊 Structured SQL",
                    "fast_faq": "⚡ Instant FAQ",
                    "small_talk": "💬 Conversational"
                }
                badge_text = route_icons.get(msg["route"], msg["route"])
                st.markdown(f'<span class="badge-route">{badge_text}</span> <small style="color:#64748b;">Latency: {msg.get("latency", 0)}s &bull; Confidence: {int(msg.get("confidence", 1.0)*100)}%</small>', unsafe_allow_html=True)

            st.markdown(msg["content"])

            if msg.get("sources"):
                with st.expander(f"📚 Grounded Citations & Sources ({len(msg['sources'])})"):
                    for s in msg["sources"]:
                        st.markdown(f"""
                        <div class="citation-card">
                            <strong>Source:</strong> <code>{s['source']}</code> &bull; <strong>Relevance Score:</strong> {s['score']}<br>
                            <em style="color:#64748b;">"{s['preview']}"</em>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat Input or Sample Button Trigger
    user_query = st.chat_input("Ask a technical question or request database analytics...")
    if sample_to_run:
        user_query = sample_to_run

    if user_query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Retrieving semantic context and synthesizing answer..."):
                route_override = None if force_route == "Auto-Detect (Semantic)" else force_route.lower().replace(" ", "_")
                result = pipeline.query(user_query, force_route=route_override, top_k=top_k)

                route_icons = {
                    "knowledge_retrieval": "🎯 Knowledge Retrieval",
                    "structured_sql": "📊 Structured SQL",
                    "fast_faq": "⚡ Instant FAQ",
                    "small_talk": "💬 Conversational"
                }
                badge_text = route_icons.get(result["route"], result["route"])
                st.markdown(f'<span class="badge-route">{badge_text}</span> <small style="color:#64748b;">Latency: {result["latency_seconds"]}s &bull; Confidence: {int(result["confidence_score"]*100)}%</small>', unsafe_allow_html=True)

                st.markdown(result["answer"])

                if result.get("sources"):
                    with st.expander(f"📚 Grounded Citations & Sources ({len(result['sources'])})"):
                        for s in result["sources"]:
                            st.markdown(f"""
                            <div class="citation-card">
                                <strong>Source:</strong> <code>{s['source']}</code> &bull; <strong>Relevance Score:</strong> {s['score']}<br>
                                <em style="color:#64748b;">"{s['preview']}"</em>
                            </div>
                            """, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "route": result["route"],
            "latency": result["latency_seconds"],
            "confidence": result["confidence_score"]
        })

# =====================================================================
# TAB 2: MULTI-SOURCE INGESTION
# =====================================================================
with tab_ingest:
    st.markdown("### 🌐 Live Web URL & Document Ingestion")
    st.markdown("Scrape web articles or upload local documents (PDF, Markdown, Text, CSV) to embed into the vector store in real-time.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔗 Web Article Scraper")
        url_input = st.text_area(
            "Enter URLs (one per line):",
            "https://en.wikipedia.org/wiki/Retrieval-augmented_generation\nhttps://en.wikipedia.org/wiki/Large_language_model",
            height=120
        )
        if st.button("🚀 Scrape & Index URLs"):
            urls = [u.strip() for u in url_input.split("\n") if u.strip()]
            if urls:
                with st.spinner(f"Fetching and indexing {len(urls)} URLs..."):
                    res = pipeline.ingest_urls(urls)
                    st.success(f"Successfully processed {res['urls_processed']} URLs into {res['chunks_indexed']} vector chunks! Total vectors in store: {res['total_store_count']}.")
            else:
                st.warning("Please provide at least one valid URL.")

    with col2:
        st.markdown("#### 📄 Local Document Uploader")
        uploaded_files = st.file_uploader(
            "Upload files (.md, .txt, .json, .csv, .pdf)",
            type=["md", "txt", "json", "csv", "pdf"],
            accept_multiple_files=True
        )
        if st.button("📥 Parse & Index Uploaded Files"):
            if uploaded_files:
                count = 0
                for uf in uploaded_files:
                    temp_path = Path("data/uploads") / uf.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uf.getbuffer())
                    res = pipeline.ingest_file(str(temp_path))
                    count += res["chunks_indexed"]
                st.success(f"Successfully indexed {len(uploaded_files)} files into {count} vector chunks!")
            else:
                st.warning("Please select files to upload.")

# =====================================================================
# TAB 3: TEXT-TO-SQL ANALYTICS
# =====================================================================
with tab_sql:
    st.markdown("### 📊 Natural Language to SQL Analytics")
    st.markdown("Query the #Gyan Labs enterprise database (`enterprise_analytics.db`) using natural language or direct SQL execution.")

    sql_col1, sql_col2 = st.columns([1, 1])

    with sql_col1:
        st.markdown("#### 💬 Ask in Natural Language")
        nl_query = st.text_input("Example: 'List all GPU clusters and their hourly cost'", "List all GPU compute nodes")
        if st.button("⚡ Run Natural Language Query"):
            res = pipeline.sql_agent.generate_and_execute(nl_query)
            st.markdown(f"**Generated SQL:** `{res['sql']}`")
            if res.get("rows"):
                df = pd.DataFrame(res["rows"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No records returned.")

    with sql_col2:
        st.markdown("#### 💻 Direct SQL Console")
        direct_sql = st.text_area("Execute Raw SQL Query:", "SELECT hub_location, SUM(gpu_count) as total_gpus, AVG(hourly_cost_usd) as avg_cost FROM compute_nodes GROUP BY hub_location;", height=100)
        if st.button("▶️ Execute SQL"):
            try:
                res = pipeline.sql_agent.execute_query(direct_sql)
                df = pd.DataFrame(res["rows"])
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")

    with st.expander("🗄️ View Database Table Schemas"):
        st.code(pipeline.sql_agent.get_schema(), language="sql")

# =====================================================================
# TAB 4: VECTOR SPACE INSPECTOR
# =====================================================================
with tab_inspector:
    st.markdown("### 🔍 Vector Store & Semantic Probe")
    st.markdown("Inspect raw chunk records, preview embeddings, and test cosine similarity distances.")

    probe_query = st.text_input("Enter probe query for vector distance analysis:", "Explain zero-trust security")
    if st.button("🔬 Probe Vector Space"):
        results = pipeline.vector_store.similarity_search(probe_query, k=6)
        if results:
            for idx, (chunk, score) in enumerate(results):
                st.markdown(f"""
                <div class="citation-card">
                    <strong>Rank #{idx+1}</strong> &bull; <strong>Cosine Similarity:</strong> <code>{score:.4f}</code> &bull; <strong>Source:</strong> <code>{chunk.metadata.get('source', 'unknown')}</code><br>
                    <p style="margin-top: 6px; font-size: 0.9rem;">{chunk.page_content}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No vector records available. Ingest documents first.")

# =====================================================================
# TAB 5: SYSTEM ARCHITECTURE
# =====================================================================
with tab_architecture:
    st.markdown("### 🏛️ #Gyan Labs Enterprise RAG Architecture")
    st.markdown("""
    The #Gyan Labs RAG platform implements a state-of-the-art modular architecture designed for high throughput, sub-50ms latency, and zero ungrounded hallucinations:
    
    1. **Ingestion & Chunking Layer:** Handles multi-source parsing (URLs, PDFs, Markdown, CSV, JSON) using recursive semantic chunking with metadata preservation.
    2. **Embedding & Vector Storage:** Utilizes dense normalized representations and hybrid in-memory vector indexing with **Maximal Marginal Relevance (MMR)** re-ranking to eliminate redundancy.
    3. **Semantic Intent Router:** Classifies user queries into Knowledge Retrieval, Text-to-SQL, Fast FAQ, and Conversational Chat.
    4. **Source Grounding Engine:** Formats verified context passages and strictly enforces factual attribution.
    """)
    st.image("https://img.shields.io/badge/Architecture-100%25%20Verified%20Open%20Source-success", use_container_width=False)
