from pathlib import Path
from typing import List

import cv2
import fitz
import numpy as np
import pytesseract


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def _parse_text_to_rows(text: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in text.splitlines():
        clean_line = line.strip()
        if not clean_line:
            continue

        cols = [token for token in clean_line.replace("|", " ").split() if token]
        if cols:
            rows.append(cols)
    return rows


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresholded


def is_ocr_required(pdf_path: Path, min_characters: int = 40) -> bool:
    document = fitz.open(pdf_path)
    try:
        sample_pages = min(len(document), 3)
        extracted_text = ""
        for page_index in range(sample_pages):
            extracted_text += document[page_index].get_text("text")
        return len(extracted_text.strip()) < min_characters
    finally:
        document.close()


def extract_rows_with_ocr(file_path: Path) -> List[List[str]]:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _extract_rows_from_pdf_with_ocr(file_path)
    if suffix in IMAGE_EXTENSIONS:
        return _extract_rows_from_image(file_path)

    raise ValueError(f"Unsupported OCR input type: {suffix}")


def _extract_rows_from_pdf_with_ocr(pdf_path: Path) -> List[List[str]]:
    rows: List[List[str]] = []
    document = fitz.open(pdf_path)

    try:
        for page in document:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            processed = _preprocess_image(image)
            text = pytesseract.image_to_string(processed, config="--psm 6")
            rows.extend(_parse_text_to_rows(text))
    finally:
        document.close()

    return rows


def _extract_rows_from_image(image_path: Path) -> List[List[str]]:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image file: {image_path}")

    processed = _preprocess_image(image)
    text = pytesseract.image_to_string(processed, config="--psm 6")
    return _parse_text_to_rows(text)
