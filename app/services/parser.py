import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages_text.append(f"--- Page {i + 1} ---\n{text.strip()}")
    return "\n\n".join(pages_text)

def extract_text_from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

def extract_text_from_txt(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")

def parse_document(filename: str, content: bytes) -> str:
    """Extract full readable text from PDF, DOCX, or TXT file."""
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(content)
    elif ext in ("txt", "md"):
        return extract_text_from_txt(content)
    else:
        # Default try utf-8
        try:
            return content.decode("utf-8")
        except Exception:
            raise ValueError(f"Unsupported file format '.{ext}'. Supported formats are: PDF, DOCX, TXT.")

