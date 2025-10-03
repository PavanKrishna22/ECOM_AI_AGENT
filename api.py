# api.py
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import sqlite3
import ollama
import pandas as pd
import re

# --- 1. SETUP ---
# Create the FastAPI application
app = FastAPI(
    title="AI E-commerce Data Agent API",
    description="An API that accepts e-commerce data questions and returns SQL queries and answers.",
    version="1.0.0"
)

# Define the structure of the incoming request data
class QueryRequest(BaseModel):
    question: str

# Define the database file and model name
DB_FILE = "ecommerce.db"
MODEL_NAME = "sqlcoder-custom"


# --- 2. CORE AI & DATABASE LOGIC (Copied from your app.py) ---

def get_predefined_query(question: str) -> str | None:
    """
    Analytics Engine: Recognizes critical questions and returns a guaranteed-correct SQL query.
    """
    normalized_question = question.lower().strip()
    cpc_match = re.search(r'(highest|lowest|max|min)\s.*cpc', normalized_question)
    
    if cpc_match:
        order = "DESC" if cpc_match.group(1) in ["highest", "max"] else "ASC"
        return f"""
            SELECT item_id, CAST(SUM(ad_spend) AS REAL) / SUM(clicks) AS cpc 
            FROM ad_sales WHERE clicks > 0 AND ad_spend > 0
            GROUP BY item_id ORDER BY cpc {order} LIMIT 1;
        """
    if 'roas' in normalized_question:
        return "SELECT CAST(SUM(ad_sales) AS REAL) / SUM(ad_spend) FROM ad_sales WHERE ad_spend > 0;"
    if 'total sales' in normalized_question:
        return "SELECT SUM(total_sales) FROM total_sales;"
    return None

def run_ai_logic(question: str):
    """
    Main agent logic: Tries the Analytics Engine first, then falls back to the LLM.
    This is a slightly modified version of your run_ai_query for API use.
    """
    # Connect to DB to get schema for the LLM
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema = "Database Schema:\n"
    for table in tables:
        table_name = table[0]
        schema += f"Table '{table_name}':\n"
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            schema += f"  - {col[1]} ({col[2]})\n"
    conn.close()

    sql_query = get_predefined_query(question)
    
    if sql_query is None:
        prompt = f"""
        You are an expert SQLite analyst. Write a single, valid SQLite query to answer the user's question.
        ### Database Schema:{schema}
        ### CRITICAL RULE:
        When a query requires grouping data (e.g., "per product"), you MUST use an aggregate function like `SUM()`.
        ### INSTRUCTIONS:
        - Output ONLY the raw SQL query.
        - If the question is irrelevant, output UNRELATED.
        ### User Question: "{question}"
        ### SQL Query:
        """
        try:
            response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0})
            sql_query = response['message']['content'].strip().replace("```sql", "").replace("```", "").replace(";", "")
            if not sql_query or "UNRELATED" in sql_query.upper():
                return {"error": "Question is irrelevant or cannot be answered."}
        except Exception as e:
            return {"error": f"LLM could not generate query: {e}"}

    try:
        conn = sqlite3.connect(DB_FILE)
        results_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if not results_df.empty:
            summary_prompt = f"Provide a short, single-sentence summary for the data, based on the original question.\nQuestion: {question}\nData:\n{results_df.to_string(index=False)}\n\nSummary:"
            summary_response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': summary_prompt}], options={'temperature': 0.5})
            summary = summary_response['message']['content'].strip()
        else:
            summary = "The query ran successfully but returned no data."
        
        # Convert DataFrame to a list of dictionaries for clean JSON output
        data_as_dict = results_df.to_dict(orient='records')
        
        return {"summary": summary, "sql_query": sql_query, "data": data_as_dict, "error": None}
    except Exception as e:
        return {"sql_query": sql_query, "data": [], "summary": f"SQL query failed. Details: {e}", "error": "execution_error"}


# --- 3. API ENDPOINT DEFINITION ---
@app.post("/query")
def process_query(request: QueryRequest):
    """
    This endpoint receives a question, runs the AI logic,
    and returns the complete analysis as a JSON response.
    """
    results = run_ai_logic(request.question)
    return results

# This block allows you to run the API directly from the command line
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)