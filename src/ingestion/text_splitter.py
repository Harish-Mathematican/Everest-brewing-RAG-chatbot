"""
#Gyan Labs - Semantic Recursive Text Splitter
=============================================
Splits large text documents into coherent chunks with overlap,
preserving document metadata, source URLs, and section headers.
"""

from typing import List, Dict, Any, Optional
import re


class DocumentChunk:
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"DocumentChunk(chars={len(self.page_content)}, source={self.metadata.get('source', 'unknown')})"


class RecursiveTextSplitter:
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "### ", "## ", ". ", "? ", "! ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """
        Recursively splits text into chunks under chunk_size with overlap.
        """
        if not text:
            return []

        chunks = []
        # Try primary paragraph splits
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If paragraph itself is too large, split by sentences
                if len(para) > self.chunk_size:
                    sentences = re.split(r"(?<=[.?!])\s+", para)
                    sub_chunk = ""
                    for sent in sentences:
                        if len(sub_chunk) + len(sent) + 1 <= self.chunk_size:
                            sub_chunk = f"{sub_chunk} {sent}" if sub_chunk else sent
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk.strip())
                            sub_chunk = sent
                    if sub_chunk:
                        current_chunk = sub_chunk
                    else:
                        current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Apply overlap between consecutive chunks if applicable
        if self.chunk_overlap > 0 and len(chunks) > 1:
            overlapped_chunks = [chunks[0]]
            for i in range(1, len(chunks)):
                prev_overlap = chunks[i - 1][-self.chunk_overlap:]
                combined = f"{prev_overlap} ... {chunks[i]}" if not chunks[i].startswith(prev_overlap[:20]) else chunks[i]
                overlapped_chunks.append(combined)
            return overlapped_chunks

        return chunks

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Splits a list of raw document dicts into DocumentChunk instances with metadata.
        """
        result_chunks = []
        for doc in documents:
            content = doc.get("content", "")
            base_metadata = doc.get("metadata", {})
            raw_chunks = self.split_text(content)

            for idx, chunk_text in enumerate(raw_chunks):
                meta = dict(base_metadata)
                meta["chunk_index"] = idx
                meta["total_chunks"] = len(raw_chunks)
                meta["chunk_length"] = len(chunk_text)
                result_chunks.append(DocumentChunk(content=chunk_text, metadata=meta))

        return result_chunks
