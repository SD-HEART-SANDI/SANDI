"""
File Name: knowledged_items.py
Purpose: Python class mode that contains searchable information of SANDI knowledge
Goals:
- Contain data we know
Architecture Decision:
@dataclass(frozen=True): represents structured and immutable/frozen data for predictable typed object 
"""

from dataclasses import dataclass
from system.models.documents import TextChunk

@dataclass(frozen=True) 
class KnowledgeItem:
    id: str #chunk_id
    name: str #program name
    program: str
    category: str
    source: str
    summary: str | None 
    text: TextChunk | None 

    