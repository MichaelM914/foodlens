# food_lens/llm_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from food_lens.utils import chunk_text, merge_multiline_items
from food_lens.smart_table_parser import extract_safe_items_from_tables

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT_TEMPLATE_MAP = {
    "dairy": """
You are a food allergen expert.

The following content is from a restaurant's allergen guide. Your job is to identify all **menu items that are safe for someone with a DAIRY allergy**.

⚠️ Very important:
- A menu item is **NOT safe** if the Milk column has "Yes", "Contains", or "May Contain".
- A menu item **IS safe** if:
  - The Milk column is completely **blank** (meaning the allergen is **NOT present**).
  - It says **"No Major Allergens Present"** anywhere in the row.

⚠️ Special note:
- If a menu item is labeled as dairy-safe but the name includes terms like “cheese”, “cream”, “milk”, “yogurt”, or “mozzarella”, keep the item but flag it with a clear warning: “❗ Double-check with the restaurant — this item’s name suggests it may contain dairy.”

Additional rules:
- Some items span multiple lines, like "Asian Sesame with & without Chicken" — treat those as **one item**.
- Deduplicate menu items if repeated.

✳️ Classification rules:
- Items like **salads**, **bowls**, **soups**, **sandwiches**, **mac & cheese**, **pizzas**, and **entrees** should go under **FULL MENU ITEMS**.
- Items like **sauces**, **toppings**, **dressings**, **individual ingredients**, and **drinks** should go under **INDIVIDUAL SAFE INGREDIENTS**.

Output format (exactly this):

--- FULL MENU ITEMS ---
(Main dishes like salads, sandwiches, bowls, entrees)

--- INDIVIDUAL SAFE INGREDIENTS ---
(Sides, drinks, toppings, sauces, breads)

Here is the allergen list:
----------------------
{text}
----------------------
"""
}

def preprocess_pdf_text(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if "CropBox missing" in stripped or "defaulting to MediaBox" in stripped:
            continue
        cleaned_lines.append(stripped)

    merged_lines = merge_multiline_items(cleaned_lines)
    return "\n".join(merged_lines)

def ask_gpt_for_safe_items(text: str, allergen: str = "dairy", max_tokens: int = 1000) -> tuple[list[str], list[str]]:
    prompt_template = PROMPT_TEMPLATE_MAP.get(allergen)
    if not prompt_template:
        raise ValueError(f"Unsupported allergen: {allergen}")

    chunks = [chunk for chunk in chunk_text(text, size=3500, overlap=200) if chunk.strip()]

    all_full_items = []
    all_sub_items = []

    for i, chunk in enumerate(chunks):
        print(f"\U0001F9E0 Processing chunk {i+1}/{len(chunks)}...")
        print(f"\n--- RAW TEXT CHUNK ---\n{chunk[:1000]}...\n")

        # Use raw text directly instead of markdown
        merged_text = chunk.strip()
        prompt = prompt_template.replace("{text}", merged_text)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        "You are an expert food allergen classifier. "
                        "You must treat a blank cell in an allergen column as SAFE (allergen not present), "
                        "not as missing or unknown data. Return only items that are confirmed safe by this rule."
                    )},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            result = response.choices[0].message.content
            full_items, sub_items = parse_gpt_result(result)
            all_full_items.extend(full_items)
            all_sub_items.extend(sub_items)
        except Exception as e:
            print(f"⚠️ GPT request failed for chunk {i+1}: {e}")

    if not all_full_items and not all_sub_items:
        try:
            fallback_full, fallback_sub = extract_safe_items_from_tables([], allergen)
            all_full_items = list(dict.fromkeys(fallback_full))
            all_sub_items = list(dict.fromkeys(fallback_sub))
        except Exception as e:
            print(f"⚠️ Fallback parser failed: {e}")

    return list(dict.fromkeys(all_full_items)), list(dict.fromkeys(all_sub_items))

def parse_gpt_result(result: str) -> tuple[list[str], list[str]]:
    lines = result.splitlines()
    full_items = []
    sub_items = []
    mode = None

    for line in lines:
        line = line.strip()
        if "--- FULL MENU ITEMS ---" in line.upper():
            mode = "full"
            continue
        elif "--- INDIVIDUAL SAFE INGREDIENTS ---" in line.upper():
            mode = "sub"
            continue
        elif not line or line.startswith("---"):
            continue
        elif line.lower() in {"no items found.", "none found."}:
            continue

        clean = line.lstrip("-•1234567890. ").strip()
        if mode == "full":
            full_items.append(clean)
        elif mode == "sub":
            sub_items.append(clean)

    return full_items, sub_items
