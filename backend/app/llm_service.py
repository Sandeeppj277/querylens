"""
LLM Service — Translates natural language to/from SQL using Google Gemini.

Two core functions:
  1. nl_to_sql()       — English question -> SQL query
  2. summarize_results() — Raw query results -> English summary
"""

import json
from google import genai
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.database import get_schema_info


def _get_client():
    """Configure and return the Gemini client instance."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file:  GEMINI_API_KEY=your-key-here"
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def _call_gemini_with_fallback(client, prompt: str) -> str:
    """Try models in sequence if the primary encounters temporary 503 capacity issues."""
    models_to_try = [GEMINI_MODEL, "gemini-2.5-flash", "gemini-1.5-flash"]
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            continue
    raise last_error if last_error else RuntimeError("No response from Gemini API.")


def nl_to_sql(question: str) -> dict:
    """
    Convert a natural language question to a SQL query.

    Returns:
        {
            "sql": "SELECT ...",
            "explanation": "This query ...",
            "chart_type": "bar" | "line" | "pie" | "table" | "number"
        }
    """
    schema = get_schema_info()
    client = _get_client()

    prompt = f"""You are an expert SQL query generator. Your job is to convert natural language 
questions into correct SQLite SQL queries.

DATABASE SCHEMA:
{schema}

RULES:
1. Generate ONLY SELECT queries. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any DDL/DML.
2. Use only the tables and columns that exist in the schema above.
3. Use proper JOINs when data spans multiple tables.
4. Use appropriate aggregations (COUNT, SUM, AVG, MAX, MIN) when the question asks for totals, averages, etc.
5. Add ORDER BY and LIMIT when the question implies ranking (e.g., "top 5", "best selling").
6. For date filtering, use SQLite date functions. The data spans from 2025-04 to 2026-10.
7. When the question mentions "last month", "this year", etc., calculate relative to the current date: 2026-10-12.
8. Always alias calculated columns with readable names (e.g., AS total_revenue).
9. FORMAT the SQL with clean indentation and line breaks across multiple lines:
   - Put SELECT, FROM, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT on their own lines.
   - In SELECT lists with multiple columns, put each column on a new indented line.
   - In JOIN clauses, put the ON condition on the same line or indented.
   - Do NOT squash the query onto a single line.
10. Return valid JSON with exactly these keys:
   - "sql": the formatted multi-line SQL query string
   - "explanation": a brief explanation of what the query does
   - "chart_type": one of "bar", "line", "pie", "table", "number" -- pick the best visualization for the result

QUESTION: {question}

Respond with ONLY valid JSON, no markdown formatting, no code fences, just the raw JSON object."""

    text = _call_gemini_with_fallback(client, prompt)

    # Clean up potential markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # remove first line
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "sql": text,
            "explanation": "Generated SQL query",
            "chart_type": "table",
        }

    return result


def summarize_results(question: str, sql: str, columns: list, rows: list) -> str:
    """
    Convert raw SQL results into a human-readable natural language summary.
    """
    client = _get_client()

    # Limit rows for the prompt to avoid token overflow
    display_rows = rows[:30]
    total_rows = len(rows)

    # Format results as a readable table
    results_text = f"Columns: {columns}\n"
    for row in display_rows:
        results_text += f"  {row}\n"
    if total_rows > 30:
        results_text += f"  ... and {total_rows - 30} more rows\n"

    prompt = f"""You are a data analyst assistant. A user asked a business question, we ran a SQL query, 
and got results. Summarize the findings in clear, natural language.

USER'S QUESTION: {question}

SQL QUERY EXECUTED: {sql}

RESULTS ({total_rows} rows):
{results_text}

RULES:
1. Write a concise 2-4 sentence summary in plain English.
2. Highlight the most important numbers and insights.
3. If results are empty, say "No data found matching your question."
4. Do NOT show raw SQL or technical jargon.
5. Use currency formatting for money values (e.g., $1,234.56).
6. Mention specific product names, customer names, or categories when relevant.

Provide ONLY the summary text, no JSON, no markdown formatting."""

    return _call_gemini_with_fallback(client, prompt)
