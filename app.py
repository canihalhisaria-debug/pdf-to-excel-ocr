import pytesseract
import cv2
import pandas as pd
from pdf2image import convert_from_path
import numpy as np

def pdf_to_excel(pdf_file):

    pages = convert_from_path(pdf_file)

    data = []

    for page in pages:
        img = cv2.cvtColor(np.array(page), cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(img)

        rows = text.split("\n")

        for row in rows:
            cols = row.split()
            data.append(cols)

    df = pd.DataFrame(data)
    df.to_excel("output.xlsx", index=False)

pdf_to_excel("sample.pdf")
