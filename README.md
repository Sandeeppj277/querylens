# 🗣️ QueryLens — Natural Language to SQL Query Generator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen?style=for-the-badge&logo=render)](https://querylens-wu6i.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google)](https://aistudio.google.com/)

🔗 **Live Deployment:** [https://querylens-wu6i.onrender.com/](https://querylens-wu6i.onrender.com/)

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

