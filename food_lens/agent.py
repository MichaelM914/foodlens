# food_lens/agent.py

import fitz
import logging
import pdfplumber
from food_lens.pdf_parser import extract_tables_from_pdf
from food_lens.html_parser import extract_text_from_html
from food_lens.llm_client import ask_gpt_for_safe_items, preprocess_pdf_text
from food_lens.utils import is_pdf_url, download_file, search_allergen_page
from food_lens.smart_table_parser import extract_safe_items_from_tables


def extract_text_from_pdf(filepath: str) -> str:
    """Use PyMuPDF to extract all visible text from a PDF."""
    doc = fitz.open(filepath)
    text = "\n\n".join([page.get_text("text") for page in doc])
    doc.close()
    return text


def analyze_restaurant_allergens(restaurant: str, allergen: str = "dairy"):
    logging.info(f"Analyzing allergens for: {restaurant.title()} (avoiding: {allergen})")

    search_result = search_allergen_page(restaurant)
    pdf_url = search_result.get("pdf_url")
    html_url = search_result.get("html_url")

    try:
        # Prefer PDF if available
        if pdf_url:
            logging.info(f"Found allergen PDF: {pdf_url}")
            local_path = download_file(pdf_url, "allergen.pdf")

            logging.info("📄 Extracting structured tables from PDF...")
            tables = extract_tables_from_pdf(local_path)

            if not tables:
                logging.warning("⚠️ No tables found in PDF — skipping directly to GPT fallback.")
                raw_text = extract_text_from_pdf(local_path)
                cleaned_text = preprocess_pdf_text(raw_text)
                return ask_gpt_for_safe_items(cleaned_text, allergen=allergen)

            logging.info("🛠️ Parsing structured allergen tables...")
            full_items, sub_items = extract_safe_items_from_tables(tables, allergen)

            if full_items or sub_items:
                logging.info("✅ Found allergen-safe items using table parser.")
                return full_items, sub_items
            else:
                logging.warning("⚠️ Table parser returned no results. Falling back to GPT...")
                raw_text = extract_text_from_pdf(local_path)
                cleaned_text = preprocess_pdf_text(raw_text)
                full_items, sub_items = ask_gpt_for_safe_items(cleaned_text, allergen=allergen)
                if full_items or sub_items:
                    logging.info("✅ GPT fallback returned results.")
                else:
                    logging.warning("⚠️ GPT fallback also returned no results.")
                return full_items, sub_items

        # If no PDF, try HTML
        if html_url:
            logging.info(f"Found allergen HTML: {html_url}")
            text = extract_text_from_html(html_url)
            cleaned_text = preprocess_pdf_text(text)

            logging.info("🧠 Fallback: Parsing HTML text with GPT...")
            full_items, sub_items = ask_gpt_for_safe_items(cleaned_text, allergen=allergen)
            return full_items, sub_items

        logging.warning("❌ No valid allergen source found (PDF or HTML).")
        return None

    except Exception as e:
        logging.error(f"Error while processing allergen data: {e}", exc_info=True)
        return None
