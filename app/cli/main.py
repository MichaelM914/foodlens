# cli/main.py

import time
import logging
from tqdm import tqdm

from food_lens.agent import analyze_restaurant_allergens
from food_lens.utils import normalize_restaurant_name
from food_lens.output import print_dairy_safe_results
from food_lens.logging_config import setup_logging


def get_restaurant_name():
    print("Welcome to FoodLens")
    name = input("Where are we eating? ").strip().lower()
    return normalize_restaurant_name(name)


def get_allergen_to_avoid():
    supported = ["dairy", "nuts"]  # Extend this list as needed
    allergen = input("What allergen should we avoid? (e.g., dairy, nuts, etc.): ").strip().lower()
    if allergen not in supported:
        print(f"⚠️ Unsupported allergen: {allergen}. Defaulting to dairy.")
        return "dairy"
    return allergen


def show_loading(message="Working...", duration=1.5):
    steps = 30
    for _ in tqdm(range(steps), desc=message, ncols=70):
        time.sleep(duration / steps)


def main():
    # Ask for log level preference first
    verbose = input("Enable verbose logging? (y/n): ").strip().lower() == "y"
    setup_logging(level=logging.DEBUG if verbose else logging.INFO)

    restaurant = get_restaurant_name()
    if not restaurant:
        print("⚠️ Please enter a valid restaurant name.")
        return

    allergen = get_allergen_to_avoid()

    start_time = time.time()
    show_loading("Looking for allergen data")

    try:
        results = analyze_restaurant_allergens(restaurant, allergen=allergen)

        if not results:
            print("❌ Could not find or analyze allergen data.")
            return

        full_items, sub_items = results
        duration = time.time() - start_time
        print(f"\n✅ Analysis completed in {duration:.2f} seconds.\n")

        print_dairy_safe_results(full_items, sub_items)

    except Exception as e:
        logging.error("An unexpected error occurred", exc_info=True)
        print(f"\n🚨 An error occurred: {e}")


if __name__ == "__main__":
    main()
