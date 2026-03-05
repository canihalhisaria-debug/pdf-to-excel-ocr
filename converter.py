from pathlib import Path
from typing import Dict, List

import pandas as pd

from ocr_engine import extract_rows_with_ocr, is_ocr_required
from pdf_extract import extract_rows_from_pdf_tables


class ConversionError(Exception):
    """Raised when conversion fails."""


def _rows_to_dataframe(rows: List[List[str]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame([{"message": "No table-like content detected."}])

    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    columns = [f"Column {idx + 1}" for idx in range(max_cols)]
    return pd.DataFrame(normalized, columns=columns)


def convert_file_to_excel(source_path: Path, output_path: Path) -> Dict[str, str]:
    source_path = Path(source_path)
    output_path = Path(output_path)

    if not source_path.exists():
        raise ConversionError(f"Input file not found: {source_path}")

    suffix = source_path.suffix.lower()

    if suffix == ".pdf":
        needs_ocr = is_ocr_required(source_path)
        rows = extract_rows_with_ocr(source_path) if needs_ocr else extract_rows_from_pdf_tables(source_path)

        if not rows and not needs_ocr:
            rows = extract_rows_with_ocr(source_path)
            needs_ocr = True
    else:
        needs_ocr = True
        rows = extract_rows_with_ocr(source_path)

    df = _rows_to_dataframe(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)

    return {
        "source_file": str(source_path),
        "excel_file": str(output_path),
        "ocr_used": str(needs_ocr),
        "rows_extracted": str(len(df.index)),
    }
