import re
import math
import time
from typing import List, Dict, Any, Tuple
from app.kb_loader import KBLoader
from app.models import RAGSource, ChatResponse

class RAGEngine:
    def __init__(self, kb_loader: KBLoader):
        self.kb_loader = kb_loader

    def _tokenize(self, text: str) -> List[str]:
        # Simple clean tokenizer converting to lowercase words
        words = re.findall(r'\b[a-zA-Z0-9%\-\.]{2,}\b', text.lower())
        stopwords = {
            "the", "and", "is", "at", "which", "on", "a", "an", "this", "for",
            "with", "to", "in", "of", "or", "by", "are", "be", "as", "from",
            "what", "how", "where", "can", "our", "all", "must", "per", "does"
        }
        return [w for w in words if w not in stopwords]

    def _compute_similarity(self, query: str, doc_text: str, doc_title: str, doc_dept: str) -> float:
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return 0.0

        doc_tokens = set(self._tokenize(doc_text + " " + doc_title + " " + doc_dept))
        
        # 1. Jaccard token overlap score
        intersection = query_tokens.intersection(doc_tokens)
        jaccard = len(intersection) / len(query_tokens) if query_tokens else 0.0

        # 2. Title boost if query words match title
        title_tokens = set(self._tokenize(doc_title))
        title_matches = len(query_tokens.intersection(title_tokens))
        title_boost = (title_matches / len(query_tokens)) * 0.4 if query_tokens else 0.0

        # 3. Exact phrase match boost
        phrase_boost = 0.3 if query.lower() in doc_text.lower() else 0.0

        # Combined score scaled to 0 - 1.0 range
        total_score = (jaccard * 0.6) + title_boost + phrase_boost
        return min(round(total_score, 4), 1.0)

    def retrieve(self, query: str, department: str = "All", top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        docs = self.kb_loader.get_documents_by_department(department)
        scored_docs = []

        for doc in docs:
            full_text = f"{doc.get('title', '')} {doc.get('subsection', '')} {doc.get('content', '')}"
            score = self._compute_similarity(query, full_text, doc.get('title', ''), doc.get('department', ''))
            if score > 0.05:  # Relevance threshold
                scored_docs.append((doc, score))

        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]

    def query(self, query: str, department: str = "All", top_k: int = 3, live_telemetry: Dict[str, Any] = None) -> ChatResponse:
        start_time = time.time()
        retrieved = self.retrieve(query, department, top_k)
        
        sources: List[RAGSource] = []
        context_blocks: List[str] = []

        for doc, score in retrieved:
            excerpt = doc.get("content", "")[:250] + "..." if len(doc.get("content", "")) > 250 else doc.get("content", "")
            sources.append(
                RAGSource(
                    id=doc.get("id", "UNK"),
                    department=doc.get("department", "General"),
                    title=doc.get("title", "Document"),
                    subsection=doc.get("subsection", "N/A"),
                    score=score,
                    excerpt=excerpt
                )
            )
            context_blocks.append(
                f"[{doc.get('id')}] {doc.get('title')} ({doc.get('department')} - {doc.get('subsection')}):\n{doc.get('content')}"
            )

        # Calculate overall confidence score based on top result score
        top_score = sources[0].score if sources else 0.0
        confidence = min(round(top_score * 1.25, 2), 0.99) if top_score > 0 else 0.15

        # Synthesize synthesized grounded answer
        if not retrieved:
            answer = (
                f"No specific Everest Brewing standard operating procedure found in the **{department}** knowledge base for your query. "
                "Please verify the department filter or try keywords like *fermentation*, *cold chain*, *OEE*, *CIP sanitization*, *Line 1*, *Line 3*, or *ESG targets*."
            )
        else:
            primary_doc = retrieved[0][0]
            answer = f"### Key Insights from Everest SOP `{primary_doc.get('id')}`:\n\n"
            answer += f"**{primary_doc.get('title')}** (*{primary_doc.get('department')} / {primary_doc.get('subsection')}*)\n\n"
            answer += f"{primary_doc.get('content')}\n\n"

            if len(retrieved) > 1:
                answer += "#### Additional Cross-Departmental Context:\n"
                for doc, score in retrieved[1:]:
                    answer += f"- **{doc.get('id')} ({doc.get('title')})**: {doc.get('content')[:180]}...\n"

            if live_telemetry:
                dept_key = department.lower().replace(" ", "_")
                if dept_key in live_telemetry:
                    answer += f"\n> **Live System Telemetry Status ({department})**: {live_telemetry[dept_key]}"

        exec_time = round((time.time() - start_time) * 1000, 2)

        return ChatResponse(
            query=query,
            answer=answer,
            sources=sources,
            department_filter=department,
            confidence_score=confidence,
            execution_time_ms=exec_time
        )
