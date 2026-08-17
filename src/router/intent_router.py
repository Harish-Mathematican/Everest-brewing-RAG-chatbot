"""
#Gyan Labs - Semantic Intent Router & Query Classifier
======================================================
Routes user queries to the optimal processing path:
- 'knowledge_retrieval': Semantic vector search across technical whitepapers and documentation.
- 'structured_sql': Natural language translation to SQL for relational tabular queries.
- 'fast_faq': High-speed cached enterprise FAQ responses.
- 'small_talk': Conversational agent for greetings and general chatter.
"""

from typing import Tuple, Dict, Any, List, Optional
import re
from src.vectorstore.embeddings import BaseEmbeddingModel, DenseSemanticEmbeddings
from src.vectorstore.chroma_store import cosine_similarity


class SemanticIntentRouter:
    def __init__(self, embedding_function: Optional[BaseEmbeddingModel] = None):
        self.embedding_function = embedding_function or DenseSemanticEmbeddings()

        # Seed Anchor Utterances for Semantic Routing
        self.route_anchors = {
            "small_talk": [
                "hello", "hi there", "hey", "good morning", "who are you",
                "what is your name", "are you an ai", "what can you do",
                "thank you", "thanks a lot", "bye", "see you later"
            ],
            "fast_faq": [
                "what is gyan labs", "where are gyan labs hubs located",
                "how do i contact the team", "what are your core hours",
                "what is hashgyan technologies", "how does your company work"
            ],
            "structured_sql": [
                "how many active servers do we have", "list all gpu clusters",
                "show total compute hours spent", "count of employees by department",
                "what is the average latency of our api", "list all ai models in production",
                "top 5 highest memory nodes", "database table counts", "show project metrics"
            ],
            "knowledge_retrieval": [
                "explain the multi-agent orchestration architecture",
                "what is our zero-trust security policy",
                "how does hybrid vector search work with mmr",
                "explain our data governance and compliance guidelines",
                "what are the benchmarks for our rag pipeline",
                "describe the hybrid cloud deployment topology"
            ]
        }

        # Precompute anchor vectors
        self.anchor_vectors: Dict[str, List[List[float]]] = {}
        for route_name, utterances in self.route_anchors.items():
            self.anchor_vectors[route_name] = self.embedding_function.embed_documents(utterances)

    def route_query(self, query: str) -> Tuple[str, float]:
        """
        Classifies incoming user query into one of the 4 routes with confidence score.
        """
        q_clean = query.strip().lower()

        # 1. Direct Regex / Heuristic fast-path
        if re.match(r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|thanks|thank\s+you|bye)[\s!.]*$", q_clean):
            return "small_talk", 0.99

        if any(w in q_clean for w in ["how many", "count of", "list all", "show table", "select *", "average cost", "highest memory", "total servers"]):
            return "structured_sql", 0.92

        # 2. Semantic Cosine Vector Routing
        query_vec = self.embedding_function.embed_query(query)
        route_scores = {}

        for route_name, vectors in self.anchor_vectors.items():
            max_sim = max(cosine_similarity(query_vec, v) for v in vectors)
            route_scores[route_name] = max_sim

        best_route = max(route_scores, key=route_scores.get)
        best_score = route_scores[best_route]

        # Default to knowledge_retrieval if ambiguous
        if best_score < 0.35:
            return "knowledge_retrieval", 0.50

        return best_route, best_score

    def get_faq_answer(self, query: str) -> Optional[str]:
        """
        Returns cached enterprise answer for standard company FAQs.
        """
        q = query.lower()
        if "what is gyan labs" in q or "what is #gyan labs" in q or "hashgyan" in q:
            return (
                "**#Gyan Labs** (part of **HashGyan Technologies**) is an advanced AI research and engineering laboratory "
                "specializing in Agentic AI Systems, Model Context Protocol (MCP) toolchains, and Enterprise Retrieval-Augmented Generation (RAG) platforms."
            )
        elif "hubs" in q or "where" in q and "located" in q:
            return (
                "**#Gyan Labs** operates across top North American technology hubs:\n"
                "• 🇨🇦 **Canada:** Toronto (ON), Montreal (QC), Vancouver (BC), Ottawa (ON), Quebec City (QC)\n"
                "• 🇺🇸 **United States:** San Francisco (CA), Seattle (WA), New York (NY), Austin (TX)"
            )
        elif "contact" in q or "support" in q:
            return "You can reach the #Gyan Labs team at **contact@gyanlabs.ai** or visit our internal developer hub at **https://gyanlabs.ai**."
        return None
