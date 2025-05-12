# food_lens/pdf_parser.py

import pdfplumber
import logging

# Suppress general pdfminer warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfminer.layout").setLevel(logging.ERROR)

def extract_tables_from_pdf(filepath: str) -> list[list[list[str]]]:
    """Extracts all tables from every page as lists of rows."""
    all_tables = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Clean each cell
                cleaned = [
                    [cell.strip() if cell else "" for cell in row]
                    for row in table
                ]
                all_tables.append(cleaned)

    return all_tables
