import fitz  # PyMuPDF
import os
import re

def extract_text(pdf_path: str) -> str:
    """
    Extract text from PDF with fallback handling.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File does not exist: {pdf_path}")

    try:
        # Try PyMuPDF first
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        if text.strip():
            return text.strip()

        raise ValueError("Empty text extracted")

    except Exception as e:
        print("⚠️ PyMuPDF failed, trying fallback...")

        # 🔁 FALLBACK → PyPDF2
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted

            if text.strip():
                return text.strip()

            raise ValueError("Fallback also failed to extract text")

        except Exception as fallback_error:
            raise RuntimeError(
                f"PDF extraction failed.\nPyMuPDF Error: {str(e)}\nPyPDF2 Error: {str(fallback_error)}"
            )
import re

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """
    text = re.sub(r'\n+', '\n', text)
    text = re.split(r'References', text, flags=re.IGNORECASE)[0]
    return text.strip()