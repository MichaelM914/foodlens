# food_lens/utils.py

import os
import re
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
SERPAPI_URL = "https://serpapi.com/search"
KEYWORDS = ["allergen", "nutrition", "menu", "pdf"]


print(f"[DEBUG] SerpAPI key loaded: {SERPAPI_API_KEY[:6]}...")  # Don't print full key


# --- Normalize user input ---
def normalize_restaurant_name(name: str) -> str:
    alias_map = {
        "cfa": "chick fil a",
        "chickfila": "chick fil a",
        "panera bread": "panera",
        "mcd": "mcdonald's",
    }
    return alias_map.get(name.lower(), name.lower())


# --- Identify PDF URLs ---
def is_pdf_url(url: str) -> bool:
    return url.lower().endswith(".pdf")


# --- Download PDF to local file ---
def download_file(url: str, filename: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download file: {url}")

    # Check if file starts with '%PDF' (magic number for PDF files)
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Downloaded file is not a valid PDF — server may be returning an HTML page")

    with open(filename, "wb") as f:
        f.write(response.content)

    return filename

# --- Search allergen page via SerpAPI ---
def search_allergen_page(restaurant_name: str, max_results: int = 10) -> dict:
    if not SERPAPI_API_KEY:
        raise EnvironmentError("SERPAPI_API_KEY not set in .env")

    query = f"{restaurant_name} allergen site:.com"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": max_results,
    }

    response = requests.get(SERPAPI_URL, params=params)
    if not response.ok:
        raise RuntimeError(f"SerpAPI failed: {response.status_code}")

    results = response.json().get("organic_results", [])

    pdf_url, html_url = None, None

    for result in results:
        link = result.get("link", "")
        title = result.get("title", "")
        if not link:
            continue

        try:
            head = requests.head(link, allow_redirects=True, timeout=5)
            content_type = head.headers.get("Content-Type", "").lower()

            if is_pdf_url(link) and "pdf" in content_type:
                print(f"[DEBUG] ✅ Valid PDF found: {link}")
                pdf_url = link
                break  # Prefer first valid PDF
            elif not html_url and "html" in content_type:
                # Test HTML body to avoid maintenance pages
                preview = requests.get(link, timeout=5).text[:500].lower()
                if "we're working on it" not in preview and "unavailable" not in preview:
                    print(f"[DEBUG] ⚠️ Valid HTML fallback found: {link}")
                    html_url = link
        except Exception as e:
            print(f"[DEBUG] ❌ Skipping broken link: {link} ({e})")

    return {
        "restaurant": restaurant_name,
        "pdf_url": pdf_url,
        "html_url": html_url,
    }



# Text preprocessing helpers

def merge_multiline_items(lines: list[str]) -> list[str]:
    merged = []
    current = ""

    for line in lines:
        # If line starts with an uppercase word and has no allergen indicators, it might be a name
        if re.match(r"^[A-Z][\w\s,&-]+$", line) and not any(word in line for word in ["Yes", "No", "Contain"]):
            if current:
                merged.append(current)
            current = line
        elif any(kw in line for kw in ["Yes", "No Major Allergens Present", "May Contain"]):
            current = f"{current} {line}".strip()
            merged.append(current)
            current = ""
        else:
            current += f" {line}"
    
    if current:
        merged.append(current)
    
    return merged


def chunk_text(text: str, size: int = 3000, overlap: int = 200) -> list[str]:
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_length + len(para) + 2 > size:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = current_chunk[-overlap:] if overlap else []
            current_length = sum(len(p) + 2 for p in current_chunk)

        current_chunk.append(para)
        current_length += len(para) + 2

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks