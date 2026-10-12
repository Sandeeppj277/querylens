"""
API route handlers for QueryLens.

Endpoints:
  POST /api/query    — Main NL→SQL→Results→Summary pipeline
  GET  /api/schema   — Return database schema for the UI explorer
  GET  /api/history  — Return query history (in-memory for now)
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.llm_service import nl_to_sql, summarize_results
from app.query_engine import execute_query, QueryValidationError
from app.database import get_schema_info

router = APIRouter(prefix="/api", tags=["query"])

# ── In-memory query history ──────────────────────────────
query_history: list[dict] = []


# ── Request / Response Models ────────────────────────────
class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        examples=["What are the top 5 best-selling products?"],
    )


class QueryResponse(BaseModel):
    question: str
    sql: str
    explanation: str
    columns: list[str]
    rows: list[list]
    row_count: int
    truncated: bool
    summary: str
    chart_type: str
    timestamp: str


class SchemaResponse(BaseModel):
    schema_sql: str


class HistoryItem(BaseModel):
    question: str
    sql: str
    summary: str
    chart_type: str
    timestamp: str
    row_count: int


# ── Endpoints ────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """
    Main pipeline: Natural language → SQL → Execute → Summarize.
    """
    question = request.question.strip()

    # Step 1: Generate SQL from natural language
    try:
        llm_result = nl_to_sql(question)
        sql = llm_result.get("sql", "")
        explanation = llm_result.get("explanation", "")
        chart_type = llm_result.get("chart_type", "table")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM failed to generate SQL: {str(e)}"
        )

    # Step 2: Execute the query safely
    try:
        result = execute_query(sql)
    except QueryValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )

    # Step 3: Generate natural language summary
    try:
        summary = summarize_results(
            question=question,
            sql=sql,
            columns=result["columns"],
            rows=result["rows"],
        )
    except Exception:
        summary = f"Query returned {result['row_count']} rows."

    # Step 4: Build response
    timestamp = datetime.now().isoformat()
    response = QueryResponse(
        question=question,
        sql=sql,
        explanation=explanation,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
        truncated=result["truncated"],
        summary=summary,
        chart_type=chart_type,
        timestamp=timestamp,
    )

    # Step 5: Save to history
    query_history.insert(0, {
        "question": question,
        "sql": sql,
        "summary": summary,
        "chart_type": chart_type,
        "timestamp": timestamp,
        "row_count": result["row_count"],
    })
    # Keep only last 50 queries
    if len(query_history) > 50:
        query_history.pop()

    return response


@router.get("/schema", response_model=SchemaResponse)
async def get_schema():
    """Return the full database schema as SQL CREATE statements."""
    try:
        schema = get_schema_info()
        return SchemaResponse(schema_sql=schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=list[HistoryItem])
async def get_history():
    """Return the last 50 queries from history."""
    return query_history
