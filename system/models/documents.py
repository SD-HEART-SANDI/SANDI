"""
File Name: documents.py
Purpose: Python class mode that contains metadata for documents for ingestion and chunking
Goals:
- Contain data we know
Architecture Decision:
@dataclass(frozen=True): represents structured and immutable/frozen data for predictable typed object 
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DocumentPage:
    page_number: int #page number of the document 
    text: str | None #page content

@dataclass(frozen=True)
class Document:
    id: str # document identification
    title: str #title of the document
    organization: str # name of organization
    published_year: int | None #the year when document is published
    source_url: str | None #reference link to the source
    pages: tuple[DocumentPage] | None #tuple for immunutable individual document page


    





