import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from food_lens.agent import analyze_restaurant_allergens


def test_agent_basic():
    restaurant = "panera"
    result = analyze_restaurant_allergens(restaurant)

    assert result is not None, "Agent returned no result."
    full_items, sub_items = result

    assert isinstance(full_items, list), "Expected list for full menu items."
    assert isinstance(sub_items, list), "Expected list for sub-items."
    assert any(full_items) or any(sub_items), "Expected at least one dairy-safe item."

    print("✅ test_agent_basic passed.")


if __name__ == "__main__":
    test_agent_basic()
