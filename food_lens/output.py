# food_lens/output.py

def print_dairy_safe_results(full_items: list[str], sub_items: list[str]) -> None:
    print("🟢 Dairy-safe menu items:")
    for item in full_items:
        print(f" - {item}")

    print("\n🟡 Safe sub-items or ingredients:")
    for item in sub_items:
        print(f" - {item}")
