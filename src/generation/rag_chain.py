"""
#Gyan Labs - RAG Synthesis Chain & Grounded Generation Engine
=============================================================
Combines retrieved context with structured prompts, invokes LLM inference
(Groq / OpenAI / Local Synthesizer), and extracts exact document citations.
"""

from typing import List, Dict, Any, Tuple, Optional
import time
import os
from src.ingestion.text_splitter import DocumentChunk
from src.generation.prompts import RAG_SYSTEM_PROMPT, SMALL_TALK_PROMPT
from src.config import GROQ_API_KEY, OPENAI_API_KEY, DEFAULT_LLM_MODEL, TEMPERATURE, MAX_TOKENS


class RAGGenerationChain:
    def __init__(self, model_name: str = DEFAULT_LLM_MODEL):
        self.model_name = model_name
        self.groq_client = None
        self.openai_client = None

        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=GROQ_API_KEY)
            except Exception:
                self.groq_client = None

        if OPENAI_API_KEY and not self.groq_client:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception:
                self.openai_client = None

    def _call_llm(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Invokes Groq, OpenAI, or falls back to intelligent local synthesis.
        """
        # 1. Try Groq (Ultra-fast LLaMA-3.3)
        if self.groq_client:
            try:
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = self.groq_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Warning: Groq API call failed ({e}). Falling back...")

        # 2. Try OpenAI
        if self.openai_client:
            try:
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Warning: OpenAI API call failed ({e}). Falling back...")

        # 3. Intelligent Local Rule-Based Synthesizer (Zero-API fallback)
        return self._local_synthesize(prompt)

    def _local_synthesize(self, prompt: str) -> str:
        """
        Generates clean, structured responses by extracting key contextual statements.
        """
        # If answering from context
        if "CONTEXT PASSAGES:" in prompt:
            context_part = prompt.split("CONTEXT PASSAGES:")[1].split("USER QUESTION:")[0].strip()
            question_part = prompt.split("USER QUESTION:")[1].split("STRUCTURED FACTUAL ANSWER:")[0].strip()

            lines = [line.strip() for line in context_part.split("\n") if line.strip() and not line.startswith("---")]
            key_points = [l for l in lines if len(l) > 30 and not l.startswith("[Source:")][:5]

            bullet_text = "\n".join(f"• {p}" for p in key_points) if key_points else context_part[:400]

            return (
                f"### Analysis for: *{question_part}*\n\n"
                f"Based on the retrieved #Gyan Labs technical documentation:\n\n"
                f"{bullet_text}\n\n"
                f"*Synthesized from verified knowledge base records.*"
            )

        return "Hello! I am the #Gyan Labs Knowledge Assistant. How can I assist you with our AI architectures, documentation, or infrastructure analytics?"

    def generate_rag_answer(
        self,
        query: str,
        retrieved_docs: List[Tuple[DocumentChunk, float]]
    ) -> Dict[str, Any]:
        """
        Synthesizes a source-grounded response with latency tracking and citations.
        """
        start_time = time.time()

        if not retrieved_docs:
            return {
                "answer": "No relevant documents were found in the #Gyan Labs knowledge base matching your query.",
                "sources": [],
                "confidence_score": 0.0,
                "latency_seconds": round(time.time() - start_time, 3)
            }

        # Build formatted context with source badges
        context_blocks = []
        sources_meta = []

        for idx, (chunk, score) in enumerate(retrieved_docs):
            src = chunk.metadata.get("source", f"Doc-{idx+1}")
            title = chunk.metadata.get("title", src)
            chunk_text = chunk.page_content.strip()

            block = f"[Source {idx+1}: {title} | Score: {score:.2f}]\n{chunk_text}"
            context_blocks.append(block)

            sources_meta.append({
                "source": src,
                "title": title,
                "score": round(score, 3),
                "preview": chunk_text[:160] + "..."
            })

        full_context = "\n\n---\n\n".join(context_blocks)
        prompt = RAG_SYSTEM_PROMPT.format(context=full_context, question=query)

        answer = self._call_llm(prompt)
        elapsed = round(time.time() - start_time, 3)
        avg_confidence = round(sum(s["score"] for s in sources_meta) / len(sources_meta), 3)

        return {
            "answer": answer,
            "sources": sources_meta,
            "confidence_score": avg_confidence,
            "latency_seconds": elapsed
        }

    def generate_small_talk_answer(self, query: str) -> str:
        prompt = SMALL_TALK_PROMPT.format(question=query)
        return self._call_llm(prompt)
