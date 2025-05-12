# food_lens/smart_table_parser.py

from typing import List, Tuple

SAFE_VALUES = {"", "no", "none", "no major allergens present"}

def find_allergen_column(headers: List[str], allergen: str) -> int:
    for i, col in enumerate(headers):
        if col and allergen.lower() in col.lower():
            return i
    return -1

def categorize_item(name: str) -> str:
    name = name.lower()
    if any(kw in name for kw in [
        "salad", "bowl", "soup", "sandwich", "entree", "wrap", "pizza", "mac", "chili"
    ]):
        return "full"
    return "sub"

def extract_safe_items_from_tables(tables: List[List[List[str]]], allergen: str = "milk") -> Tuple[List[str], List[str]]:
    full_items, sub_items = [], []

    for table in tables:
        if not table or len(table) < 2:
            continue

        headers = table[0]
        allergen_col = find_allergen_column(headers, allergen)
        name_col = 0  # assume first column is the name

        if allergen_col == -1:
            continue

        for row in table[1:]:
            if len(row) <= max(name_col, allergen_col):
                continue

            name = row[name_col].strip()
            value = row[allergen_col].strip().lower()

            if value in SAFE_VALUES:
                if categorize_item(name) == "full":
                    full_items.append(name)
                else:
                    sub_items.append(name)

    return list(dict.fromkeys(full_items)), list(dict.fromkeys(sub_items))
