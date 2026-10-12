# 🗣️ QueryLens — Natural Language to SQL Query Generator

QueryLens bridges the gap between non-technical users and relational databases. Ask any business question in plain English, and QueryLens:
1. Translates the question into optimized, safe SQL using Google Gemini LLM
2. Executes the query safely against an e-commerce database (SQLite)
3. Renders the raw data in an interactive table and multi-type chart (Chart.js)
4. Generates a natural language executive summary

---

## ✨ Features

- **Conversational SQL Generation**: Translates natural language questions to multi-table joins, aggregations, and subqueries.
- **Safety First**: Restricts queries to `SELECT`-only and blocks destructive SQL injections (`DROP`, `DELETE`, `ALTER`, etc.).
- **Vivid Glassmorphism UI**: High-contrast modern glass UI with responsive sidebars, animated ambient light, and collapsible drawers.
- **Multi-Line Syntax Highlighting**: Colorized SQL with separate lines for clauses, columns, and joins via `highlight.js`.
- **Dynamic Charts**: Automatically picks and renders the right visualization (Bar, Line, or Pie) using Chart.js.
- **Export Data**: One-click CSV export of generated results.
- **Self-Contained Fullstack**: FastAPI serves both the REST API and the static frontend with zero complex build setup.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy
- **LLM Engine**: Google Gemini API (`gemini-3.8-flash` with multi-model fallback)
- **Database**: SQLite (6 relational tables: categories, products, customers, orders, order items, reviews)
- **Frontend**: HTML5, CSS3 Glassmorphism, Vanilla JavaScript, Chart.js, Highlight.js

---

## 🚀 Quickstart (Local Run)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/querylens.git
cd querylens
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

### 5. Seed the database (First time only)
```bash
python -c "import sys; sys.path.insert(0, 'backend'); from app.seed import seed; seed()"
```

### 6. Run the server
```bash
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
Open **`http://localhost:8000`** in your browser.

---


   - **Start Command**: `python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: `your_gemini_key`
   - `GEMINI_MODEL`: `gemini-3.8-flash`
