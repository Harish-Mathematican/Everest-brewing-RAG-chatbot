import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("everest_rag.kb_loader")

class KBLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.documents: List[Dict[str, Any]] = []
        self.load_all_documents()

    def load_all_documents(self) -> List[Dict[str, Any]]:
        self.documents = []
        if not os.path.exists(self.data_dir):
            logger.warning(f"Knowledge Base directory {self.data_dir} does not exist.")
            return self.documents

        for filename in sorted(os.listdir(self.data_dir)):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.documents.extend(data)
                        elif isinstance(data, dict):
                            self.documents.append(data)
                    logger.info(f"Loaded {filename} successfully ({len(data)} items).")
                except Exception as e:
                    logger.error(f"Error reading {filepath}: {e}")

        logger.info(f"Total Knowledge Base documents loaded: {len(self.documents)}")
        return self.documents

    def get_documents_by_department(self, department: str) -> List[Dict[str, Any]]:
        if not department or department.lower() == "all":
            return self.documents
        return [
            doc for doc in self.documents
            if doc.get("department", "").lower() == department.lower()
        ]

    def add_live_document(self, doc: Dict[str, Any]):
        # Check if ID already exists and update, else append
        existing_idx = next((i for i, d in enumerate(self.documents) if d.get("id") == doc.get("id")), None)
        if existing_idx is not None:
            self.documents[existing_idx] = doc
        else:
            self.documents.append(doc)
        logger.info(f"Live document added/updated: {doc.get('id')} - {doc.get('title')}")
