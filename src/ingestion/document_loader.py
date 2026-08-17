"""
#Gyan Labs - Universal Document Loader
======================================
Loads and parses local documents (Markdown, Text, PDF, JSON, CSV)
with metadata enrichment (author, date, tags, filename).
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import json


class UniversalDocumentLoader:
    def __init__(self, supported_extensions: Optional[List[str]] = None):
        self.supported_extensions = supported_extensions or [".md", ".txt", ".json", ".csv", ".pdf"]

    def load_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a single file and extracts content and metadata.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file format '{ext}'. Supported: {self.supported_extensions}")

        base_meta = {
            "source": str(path.name),
            "file_path": str(path.resolve()),
            "file_type": ext[1:],
            "file_size_bytes": path.stat().st_size
        }

        # 1. Plain Text / Markdown
        if ext in [".md", ".txt"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return [{"content": content, "metadata": base_meta}]

        # 2. JSON Document
        elif ext == ".json":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            if isinstance(data, list):
                docs = []
                for idx, item in enumerate(data):
                    item_str = json.dumps(item, indent=2) if isinstance(item, dict) else str(item)
                    meta = dict(base_meta)
                    meta["record_index"] = idx
                    docs.append({"content": item_str, "metadata": meta})
                return docs
            elif isinstance(data, dict):
                # Check for standard document structure
                content = data.get("content") or data.get("text") or json.dumps(data, indent=2)
                meta = dict(base_meta)
                if "title" in data:
                    meta["title"] = data["title"]
                if "category" in data:
                    meta["category"] = data["category"]
                return [{"content": content, "metadata": meta}]

        # 3. CSV Dataset
        elif ext == ".csv":
            import csv
            docs = []
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
                    meta = dict(base_meta)
                    meta["row_index"] = idx
                    docs.append({"content": row_text, "metadata": meta})
            return docs

        # 4. PDF (Optional fallback parser)
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                pages_content = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        meta = dict(base_meta)
                        meta["page_number"] = idx + 1
                        pages_content.append({"content": page_text, "metadata": meta})
                return pages_content if pages_content else [{"content": f"PDF content placeholder for {path.name}", "metadata": base_meta}]
            except ImportError:
                return [{"content": f"[PDF File: {path.name}] - Install pypdf for deep binary extraction.", "metadata": base_meta}]

        return []

    def load_directory(self, dir_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Loads all supported documents from a directory.
        """
        p = Path(dir_path)
        if not p.exists() or not p.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        pattern = "**/*" if recursive else "*"
        all_docs = []

        for item in p.glob(pattern):
            if item.is_file() and item.suffix.lower() in self.supported_extensions:
                try:
                    loaded = self.load_file(str(item))
                    all_docs.extend(loaded)
                except Exception as e:
                    print(f"Warning: Failed to load {item}: {e}")

        return all_docs
