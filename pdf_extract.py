from pathlib import Path
from typing import List

import pdfplumber


def extract_rows_from_pdf_tables(pdf_path: Path) -> List[List[str]]:
    rows: List[List[str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    cleaned = [cell.strip() if isinstance(cell, str) else "" for cell in row]
                    if any(cleaned):
                        rows.append(cleaned)

            if not tables:
                text = page.extract_text() or ""
                for line in text.splitlines():
                    tokens = [token for token in line.strip().split() if token]
                    if len(tokens) > 1:
                        rows.append(tokens)

    return rows
