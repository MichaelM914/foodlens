# 🧼 FoodLens

**FoodLens** helps users quickly find allergen-safe menu items at restaurants by analyzing publicly available allergen or nutrition guides (PDF or HTML). Powered by GPT and SerpAPI.

---

## 🧠 What It Does

Given a restaurant name and allergen (e.g., "Panera" and "dairy"), FoodLens will:

- Search for the restaurant’s allergen guide (PDF or web)
- Extract and clean the menu content
- Identify **safe items** that do **not** contain the selected allergen
- Display results in categories:
  - ✅ Full menu items (e.g., salads, bowls)
  - ⚠️ Individual safe ingredients (e.g., toppings, drinks)

---

## 🚀 How to Run

### 1. 📦 Install dependencies

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

pip install -r requirements.txt
```

### 2. 🔐 Set up environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your-openai-api-key
SERPAPI_API_KEY=your-serpapi-api-key
```

Never commit this file — it’s already in `.gitignore`.

---

## 🖥️ Usage

### 🧪 CLI Mode

```bash
python app/run_cli.py
```

- You'll be prompted to enter:
  - The restaurant name
  - The allergen to avoid (e.g. dairy)
  - Optional verbose logging

### 🌐 Web UI (Streamlit)

```bash
PYTHONPATH=. streamlit run app/web_ui.py
```

- Simple text input and dropdown selection
- Auto-formatted results

---

## 🧪 Running Tests

```bash
python tests/test_agent.py
```

(You can add more tests to the `tests/` directory.)

---

## 🤝 Contributions

Pull requests welcome! Feel free to open issues for bugs, ideas, or feature requests.

---

## 📜 License

MIT License (or your preferred license)

---

## 🙋‍♀️ Built for

This tool was created to support safe dining for those with food allergies — especially helpful for families and caretakers who need confidence when eating out.
