from pathlib import Path

from pypdf import PdfReader


class PDFLoader:

    @staticmethod
    def load(file_path: str) -> str:

        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text())

        return "\n".join(pages)