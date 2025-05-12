# food_lens/html_parser.py

import requests
from bs4 import BeautifulSoup


def extract_text_from_html(url: str) -> str:
    response = requests.get(url)
    if not response.ok:
        raise RuntimeError(f"Failed to fetch HTML: {url}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Try to extract only main content
    content = soup.find("main") or soup.find("body") or soup
    raw_text = content.get_text(separator="\n")
    
    lines = [line.strip() for line in raw_text.splitlines()]
    cleaned = [line for line in lines if line]  # Remove blank lines

    return "\n".join(cleaned)
