import streamlit as st
import sqlite3
import ollama
import pandas as pd
import plotly.express as px
import time
import re

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ENHANCED UI STYLING WITH MORE ANIMATIONS ---
def load_css():
    """Injects custom CSS for a minimalist, animated, gradient UI with more effects."""
    st.markdown("""
    <style>
        /* Define theme variables */
        :root {
            --primary-bg: #000000;
            --secondary-bg: rgba(28, 28, 30, 0.7); /* Semi-transparent for glass effect */
            --text-primary: #F5F5F7;
            --text-secondary: #8E8E93;
            --accent-color: #0A84FF; /* Apple-style blue */
            --border-color: rgba(56, 56, 58, 0.5);
        }

        html, body, [class*="st-"], [class*="css-"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        /* Animated Gradient Background */
        @keyframes gradient-animation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .stApp {
            background: linear-gradient(-45deg, #0d1a26, #000000, #1a1a2d, #000000);
            background-size: 400% 400%;
            animation: gradient-animation 25s ease infinite;
            color: var(--text-primary);
        }
        
        /* Entrance animation for elements */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main > div { animation: fadeInUp 0.8s ease-out forwards; }

        /* Clean title styling */
        h1 { font-weight: 700; letter-spacing: -0.5px; }
        h3 { font-weight: 600; }

        /* Minimalist text area with focus effect */
        .stTextArea textarea {
            background-color: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 17px;
            padding: 12px;
            backdrop-filter: blur(10px);
        }
        
        /* --- ENHANCED BUTTON STYLING --- */
        @keyframes glow {
            0% { box-shadow: 0 0 5px rgba(10, 132, 255, 0.3); }
            50% { box-shadow: 0 0 20px rgba(10, 132, 255, 0.8); }
            100% { box-shadow: 0 0 5px rgba(10, 132, 255, 0.3); }
        }
        .stButton button {
            background-color: var(--accent-color);
            color: white;
            border-radius: 10px;
            padding: 12px 24px;
            border: none;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.15s ease, box-shadow 0.3s ease;
        }
        .stButton button:hover {
            transform: scale(1.03);
            animation: glow 1.5s infinite;
        }
        .stButton button:active { transform: scale(0.98); }
        
        /* Style for the results container "card" */
        .st-emotion-cache-1r6slb0 {
            background-color: var(--secondary-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color) !important;
            border-radius: 16px !important;
            padding: 24px;
            animation: fadeInUp 0.8s ease-out forwards;
        }
        .stSpinner > div > div { border-top-color: var(--accent-color) !important; }
    </style>
    """, unsafe_allow_html=True)

load_css()


# --- 3. DATABASE AND AI CONFIGURATION ---
DB_FILE = "ecommerce.db"
MODEL_NAME = "sqlcoder-custom"

@st.cache_resource
def get_schema():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # ... (rest of the function is unchanged)
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
    return schema

# --- 4. THE HYBRID AI AGENT ---

def get_predefined_query(question: str) -> str | None:
    # ... (function is unchanged)
    normalized_question = question.lower().strip()
    cpc_match = re.search(r'(highest|lowest|max|min)\s.*cpc', normalized_question)
    
    if cpc_match:
        order = "DESC" if cpc_match.group(1) in ["highest", "max"] else "ASC"
        print("--- ANALYTICS ENGINE: Using pre-defined query for CPC ---")
        return f"""
            SELECT item_id, CAST(SUM(ad_spend) AS REAL) / SUM(clicks) AS cpc 
            FROM ad_sales WHERE clicks > 0 AND ad_spend > 0
            GROUP BY item_id ORDER BY cpc {order} LIMIT 1;
        """
    if 'roas' in normalized_question:
        print("--- ANALYTICS ENGINE: Using pre-defined query for RoAS ---")
        return "SELECT CAST(SUM(ad_sales) AS REAL) / SUM(ad_spend) FROM ad_sales WHERE ad_spend > 0;"
    if 'total sales' in normalized_question:
        print("--- ANALYTICS ENGINE: Using pre-defined query for Total Sales ---")
        return "SELECT SUM(total_sales) FROM total_sales;"
    return None

def run_ai_query(question: str, schema: str):
    sql_query = get_predefined_query(question)
    
    if sql_query is None:
        print("--- GENERATIVE EXPLORER: Using LLM for query generation ---")
        prompt = f"""
        You are an expert SQLite data analyst. Write a single, valid SQLite query to answer the user's question.
        ### Database Schema:
        {schema}
        ### CRITICAL RULE:
        When a query requires grouping data (e.g., "per product"), you MUST use an aggregate function like `SUM()` on the columns being calculated.
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
                return {"summary": "I can only answer questions related to e-commerce data.", "sql_query": "N/A", "data": pd.DataFrame(), "error": "irrelevant"}
        except Exception as e:
            return {"sql_query": "Error during LLM call.", "data": pd.DataFrame(), "summary": f"Could not generate query: {e}", "error": "llm_error"}

    try:
        conn = sqlite3.connect(DB_FILE)
        results_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if not results_df.empty:
            # --- NEW SUMMARY PROMPT ---
            # Explicitly tells the AI to AVOID currency symbols.
            summary_prompt = f"""
            Provide a short, single-sentence summary for the data, based on the original question.
            CRITICAL: Do NOT use any currency symbols like '$' or '₹'. State the numbers directly.
            
            Question: {question}
            Data:
            {results_df.to_string(index=False)}
            
            Summary:
            """
            summary_response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': summary_prompt}], options={'temperature': 0.5})
            summary = summary_response['message']['content'].strip()
        else:
            summary = "The query ran successfully but returned no data."
        return {"sql_query": sql_query, "data": results_df, "summary": summary, "error": None}
    except Exception as e:
        return {"sql_query": sql_query, "data": pd.DataFrame(), "summary": f"SQL query failed. Details: {e}", "error": "execution_error"}

# --- 5. VISUALIZATION ENGINE (No changes) ---
def create_visualization(df: pd.DataFrame):
    # ... (function is unchanged)
    if df is None or df.empty: return None
    template = "plotly_dark"
    numeric_cols = df.select_dtypes(include=['number']).columns
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    if len(df) == 1 and len(numeric_cols) == 1: return None
    try:
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
            return px.line(df, x=date_cols[0], y=numeric_cols[0], title="Time Series Analysis", markers=True, template=template)
        elif len(string_cols) > 0 and len(numeric_cols) > 0:
            return px.bar(df, x=string_cols[0], y=numeric_cols[0], title=f"Analysis by {string_cols[0]}", template=template, color=numeric_cols[0], color_continuous_scale=px.colors.sequential.Viridis)
        elif len(string_cols) > 0 and len(numeric_cols) == 1 and 2 < len(df) < 10:
            return px.pie(df, names=string_cols[0], values=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}", template=template, hole=0.3)
    except Exception: return None
    return None

# --- NEW: Helper function for the typing effect ---
def stream_text(text):
    """Yields text word by word for a typing effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05) # Adjust typing speed here


# --- 6. MAIN STREAMLIT UI LAYOUT ---
st.title("AI Data Analyst")
st.markdown("<span style='color: var(--text-secondary);'>Ask a question to get answers, data, and visualizations.</span>", unsafe_allow_html=True)

question = st.text_area("Your question:", height=120, placeholder="e.g., What were my total sales per day? or Which product had the highest CPC?", label_visibility="collapsed")

if st.button("Generate Answer"):
    if question:
        with st.spinner("Analyzing..."):
            st.session_state.results = run_ai_query(question, get_schema())
    else:
        st.warning("Please enter a question.")

# --- DYNAMIC RESULT DISPLAY WITH TYPING EFFECT ---
if 'results' in st.session_state:
    results = st.session_state.results
    st.divider()

    if results['error']:
        st.error(f"🤖 **An error occurred:** {results['summary']}")
        if results['error'] == 'execution_error':
            st.code(results['sql_query'], language='sql')
    else:
        with st.container(border=True):
            st.subheader("Analysis")
            
            # --- THIS IS THE NEW TYPING EFFECT BLOCK ---
            st.write_stream(stream_text(f"### 🤖   {results['summary']}"))
            
            fig = create_visualization(results['data'])
            
            if fig:
                viz_col, data_col = st.columns([0.65, 0.35])
                with viz_col:
                    st.subheader("Visualization")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="var(--text-primary)", xaxis=dict(gridcolor='var(--border-color)'), yaxis=dict(gridcolor='var(--border-color)'))
                    st.plotly_chart(fig, use_container_width=True)
                with data_col:
                    st.subheader("Data")
                    st.dataframe(results['data'], use_container_width=True)
            else:
                st.subheader("Data")
                st.dataframe(results['data'], use_container_width=True)

            with st.expander("View Generated SQL Query"):
                st.code(results['sql_query'], language='sql')