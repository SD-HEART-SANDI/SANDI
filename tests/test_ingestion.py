
"""
File: tests/test_ingestion.py
Purpose: Generated unit testing for PDF extraction.
"""

import pytest
import pymupdf

from pathlib import Path
from system.rag.ingestion import extract_pdf, ingest_pdf
from system.models.documents import Document, DocumentPage


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a temporary two-page PDF with known content."""

    pdf_path = tmp_path / "sample.pdf"

    with pymupdf.open() as pdf:
        page1 = pdf.new_page()
        page1.insert_text(
            (72, 72),
            "CalFresh provides food assistance."
        )

        page2 = pdf.new_page()
        page2.insert_text(
            (72, 72),
            "Medi-Cal provides health coverage."
        )

        pdf.save(pdf_path)

    return pdf_path


def test_extract_returns_tuple(sample_pdf):
    result = extract_pdf(sample_pdf)

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_extract_returns_document_pages(sample_pdf):
    result = extract_pdf(sample_pdf)

    assert all(isinstance(page, DocumentPage) for page in result)


def test_page_numbering(sample_pdf):
    result = extract_pdf(sample_pdf)

    assert result[0].page_number == 1
    assert result[1].page_number == 2


def test_extracted_text(sample_pdf):
    result = extract_pdf(sample_pdf)

    assert "CalFresh provides food assistance." in result[0].text
    assert "Medi-Cal provides health coverage." in result[1].text


def test_missing_pdf(tmp_path):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_pdf(missing_path)


def test_ingest_pdf_constructs_document(sample_pdf):
    """Verify PDF ingestion preserves metadata and extracted pages."""

    document = ingest_pdf(
        file_path=sample_pdf,
        id="TEST-001",
        title="Sample Eligibility Guide",
        organization="Test Agency",
        published_year=2026,
        source_url="https://example.org/guide.pdf"
    )

    # Validate document object
    assert isinstance(document, Document)

    # Validate caller-supplied metadata
    assert document.id == "TEST-001"
    assert document.title == "Sample Eligibility Guide"
    assert document.organization == "Test Agency"
    assert document.published_year == 2026
    assert document.source_url == "https://example.org/guide.pdf"

    # Validate extracted pages
    assert isinstance(document.pages, tuple)
    assert len(document.pages) == 2

    # Validate page numbering and text
    assert document.pages[0].page_number == 1
    assert document.pages[1].page_number == 2

    assert "CalFresh provides food assistance." in document.pages[0].text
    assert "Medi-Cal provides health coverage." in document.pages[1].text


#TEST: Ingestion Output
document = ingest_pdf(
    file_path=Path("data/raw/Food_CalFresh_CalSAWS_Overview.docx"),
    id="TEST-001",
    title="Sample Eligibility Guide",
    organization="Test Agency",
    published_year=2026,
    source_url=None
)

# Document metadata
print("Document ID:", document.id)
print("Title:", document.title)
print("Organization:", document.organization)
print("Total pages:", len(document.pages))

# Extracted content
for page in document.pages:
    print(f"\n--- Page {page.page_number} ---")
    print(page.text[:500])  # Preview first 500 characters