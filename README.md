# ECOM_AI_AGENT

# 🧠 AI E-commerce Data Agent

An interactive web app that lets you ask **natural language questions** about your e-commerce sales data — with instant insights, SQL explanations, and interactive visualizations. It’s **private by design**, using a local Large Language Model (LLM) powered by **Ollama**.


<img width="1918" height="866" alt="image" src="https://github.com/user-attachments/assets/3c083193-bc85-4df3-b192-7bc2548c2efa" />
<img width="1917" height="866" alt="image" src="https://github.com/user-attachments/assets/58e6a077-812a-4e5f-a813-becc2a60ca05" />
<img width="1918" height="868" alt="image" src="https://github.com/user-attachments/assets/90bb3642-3e5c-4fc9-8074-7a586c435e0a" />
![Uploading image.png…]()


## 📌 Project Summary

This system combines two intelligent engines:

🔹 **Analytics Engine** — fast and accurate answers for predefined business metrics (e.g., ROAS, CPC, Total Sales).  
🔹 **Generative SQL Explorer** — powered by the local `sqlcoder` LLM, answering free-form data questions with on-the-fly SQL generation.

💡 Results are displayed in a modern, interactive **Streamlit dashboard** with **Plotly** visualizations.

---

## 🎯 Key Features

| Feature                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| 💬 Natural Language Input   | Ask anything from “Top product last month” to “Total sales by region”       |
| ⚙️ Hybrid AI Logic           | Combines rule-based SQL + LLM-based dynamic SQL                            |
| 📊 Auto Visualizations      | Uses Plotly to generate bar, line, and pie charts from results              |
| 🔒 Fully Local + Private    | No cloud calls, no tracking — all data stays on your machine                |
| 🧩 Modular Architecture     | Streamlit UI (frontend) + FastAPI backend + SQLite database                 |
| 🔁 Reusable & Scalable      | Easily extendable with new datasets, models, or analytics rules             |

---

## 🧱 Architecture

```text
[User Input]
      ↓
[Streamlit Frontend] ───→ [FastAPI Backend]
                                 ↓
                [Analytics Engine / SQLCoder LLM]
                                 ↓
                       [SQLite Database]
                                 ↓
               [Result → Chart + Table + SQL Output]
````

---

## 🧰 Tech Stack

| Layer       | Tools & Libraries       |
| ----------- | ----------------------- |
| Frontend    | Streamlit               |
| Backend     | FastAPI, Uvicorn        |
| AI / LLM    | Ollama, sqlcoder (GGUF) |
| Data Engine | SQLite, Pandas          |
| Charts      | Plotly                  |
| Language    | Python 3.8+             |

---

## 📁 Folder Structure

```
📦 ecommerce-ai-agent/
├── api.py
├── app.py
├── create_db.py
├── requirements.txt
├── Modelfile
├── sqlcoder-7b-q5_k_m.gguf
├── Product-Level Ad Sales and Metrics.csv
├── Product-Level Eligibility Table.csv
├── Product-Level Total Sales and Metrics.csv
└── README.md
```

---

## 🧠 Setup: LLM via Ollama

### 1. 📥 Download Model

Manually download the model file:
👉 [sqlcoder-7b-q5\_k\_m.gguf (Hugging Face)](https://huggingface.co/jeongs/sqlcoder-7b-q5_K_M-GGUF/resolve/main/sqlcoder-7b-q5_k_m.gguf)

Save it in your project folder.

### 2. 📝 Create `Modelfile`

```txt
FROM ./sqlcoder-7b-q5_k_m.gguf
```

### 3. 🛠️ Build and Run with Ollama

```bash
ollama create sqlcoder-custom -f Modelfile
ollama run sqlcoder-custom
```

Type `/bye` to exit the prompt once it's running.

---

## ⚙️ Installation Guide

### 1. ✅ Install Prerequisites

* [Python 3.8+](https://www.python.org/downloads/)
* [Ollama](https://ollama.ai/)

### 2. 📦 Create and Activate Virtual Environment

```bash
python -m venv venv
# Activate:
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 📄 Install Dependencies

Create `requirements.txt`:

```txt
fastapi
uvicorn[standard]
pydantic
pandas
ollama
streamlit
plotly
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the App

### Step 1: 📊 Create the SQLite Database

```bash
python create_db.py
```

### Step 2: ⚙️ Start the FastAPI Backend

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test endpoints.

### Step 3: 🖥️ Launch the Streamlit Frontend

```bash
streamlit run app.py
```

Visit: [http://localhost:8501](http://localhost:8501)

---

## 💡 Example Queries to Try

* "What are my total sales?"
* "Which product had the highest ROAS last month?"
* "Show average CPC by product"
* "List all products eligible for ads"
* "Compare total spend across categories"

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

* [Ollama](https://ollama.ai/) – Local model runner
* [Hugging Face](https://huggingface.co) – Model hosting
* [Streamlit](https://streamlit.io) – App framework
* [FastAPI](https://fastapi.tiangolo.com/) – API framework

```

---

Let me know if you'd like a `LICENSE` file or badges (e.g., Python version, license, stars) for the top of the README.
```
