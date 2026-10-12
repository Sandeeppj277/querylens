"""
Safe SQL execution engine.

Validates that only SELECT queries run, enforces row limits, and returns
structured results (columns + rows) ready for the API response.
"""

import re
from sqlalchemy import text
from app.database import engine
from app.config import ALLOWED_SQL_PREFIXES, MAX_RESULT_ROWS


class QueryValidationError(Exception):
    """Raised when a query fails safety validation."""
    pass


def validate_query(sql: str) -> str:
    """
    Validate and sanitize the SQL query.

    Raises QueryValidationError if the query is not a safe SELECT.
    Returns the cleaned SQL string.
    """
    cleaned = sql.strip().rstrip(";").strip()

    if not cleaned:
        raise QueryValidationError("Empty query received.")

    # Check it starts with SELECT
    first_word = cleaned.split()[0].lower()
    if first_word not in ALLOWED_SQL_PREFIXES:
        raise QueryValidationError(
            f"Only SELECT queries are allowed. Got: '{first_word.upper()}...'"
        )

    # Block dangerous keywords even inside a SELECT (subquery attacks)
    dangerous_patterns = [
        r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b',
        r'\bDROP\b', r'\bALTER\b', r'\bCREATE\b',
        r'\bTRUNCATE\b', r'\bEXEC\b', r'\bEXECUTE\b',
        r'\bGRANT\b', r'\bREVOKE\b', r'\bATTACH\b',
        r'\bDETACH\b', r'\bPRAGMA\b',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            keyword = re.search(pattern, cleaned, re.IGNORECASE).group()
            raise QueryValidationError(
                f"Forbidden keyword detected: '{keyword}'. Only read queries are allowed."
            )

    return cleaned


def execute_query(sql: str) -> dict:
    """
    Execute a validated SQL query and return structured results.

    Returns:
        {
            "columns": ["col1", "col2", ...],
            "rows": [[val1, val2, ...], ...],
            "row_count": int,
            "truncated": bool
        }
    """
    clean_sql = validate_query(sql)

    with engine.connect() as conn:
        result = conn.execute(text(clean_sql))

        columns = list(result.keys())
        rows = [list(row) for row in result.fetchmany(MAX_RESULT_ROWS + 1)]

        truncated = len(rows) > MAX_RESULT_ROWS
        if truncated:
            rows = rows[:MAX_RESULT_ROWS]

        # Convert non-serializable types to strings
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                if val is not None and not isinstance(val, (int, float, str, bool)):
                    rows[i][j] = str(val)

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
        }
