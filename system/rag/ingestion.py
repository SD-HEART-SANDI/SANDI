#Purpose: Load and extract text
"""
File Name: ingestion.py
Goals:
-read and extract PDF files
-attach source metadata
-reject unsupported files
-Accept a local PDF path and return a Document object containing extracted pages.
-return structured document objects
"""

import pymupdf, pathlib
from pathlib import Path
from system.models.documents import  Document, DocumentPage


def extract_pdf(file_path: Path) -> tuple[DocumentPage,...]: 

    #list of document pages for mutability -> flexibility
    page_list : list[DocumentPage] = [ ]

    #Opens document
    if not file_path.exists():
       raise FileNotFoundError(f"INGESTION ERROR: File {file_path} does not exists")
    try:
        doc = pymupdf.open(file_path) #open document
    except FileNotFoundError:
        raise FileNotFoundError("INGESTION ERROR: File  does not exist or invalid")
    
    #Extract all document text list comprehension in un-natural order
    for i, page in enumerate (doc, start=1):

        #increase page number every iteratation
        text = page.get_text() #get plain text
        #Construct and add one DocumentPage to form a document
        doc_page = DocumentPage(page_number = i,text = text)
        page_list.append(doc_page)

    return tuple(page_list)

#TODO
def ingest_pdf(file_path: Path) -> Document:
    pass


