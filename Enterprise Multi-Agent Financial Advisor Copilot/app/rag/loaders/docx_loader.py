from docx import Document


class DOCXLoader:

    @staticmethod
    def load(file_path: str) -> str:

        document = Document(file_path)

        paragraphs = [
            p.text
            for p in document.paragraphs
        ]

        return "\n".join(paragraphs)