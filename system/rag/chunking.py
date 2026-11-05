#Purpose: Divided extract texts into retrievable information
"""
Filename: chunking.py
Goals:
-split text by headings, paragraphs, or size
- convert extracted PDF pages into searchable knowledge units while preserving their source information
Architecture Decision:
Detail of ingestion pipeline to extract clear and managaeble segment/chunkss of pdfs
"""

#Function Signature
from system.models.documents import TextChunk, DocumentPage, Document
from system.rag.ingestion import extract_pdf, ingest_pdf
from system.models.knowledge_items import KnowledgeItem

#Text Chunk Modelx
#TODO

def chunk_document(document: Document) ->  tuple[TextChunk,...]:
    """
    Description: Convert each nonempty DocumentPage into one TextChunk
    """
    #Inialization
    text = [] #text list
    chunks : TextChunk = []

    #Interate through each page in document
    for index, page in enumerate(document.pages, start=0):

  
        #Check for all white space
        #Extract page's text and clean text
        text = page.text.strip()
        if not text:
            print(f"CHUNKING: Extracted text is not valid and empty")
            continue #skip the invalid page
        
        document_page = document.pages[index]

        #Insert page's text into Text Chunk tuple with generated unique id and inherit source metadata
        chunk = TextChunk(
            id=document.id + str(document_page.page_number) + str(index),
            document_id=document.id,
            page_number=document_page.page_number,
            text=text,
            chunk_index=index,
        )

        chunks.append(chunk)

    #Return tuple
    return tuple(chunks) #convert text list to tupe


#TODO
def chunks_to_knowledge(document: Document, chunks: tuple[TextChunk,...]) -> list[KnowledgeItem]:

    #Init
    knowledge_list : list [KnowledgeItem] = [ ]

    #Iterate through each chunks
    for index, chunk in enumerate (chunks, start=0):
        #Construct KnowledgeItem
        knowledge_item = KnowledgeItem(
            id=chunk.id,
            name=document.title,
            program=document.program,
            category=document.category,
            source=document.source_url,
            summary=None,
            text=chunk
        ) 

        knowledge_list.append(knowledge_item)

    return knowledge_list

