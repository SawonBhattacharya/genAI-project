# 📊 ReAct SQL Agent with Streamlit UI

## 🔎 Project Overview

This project implements an **LLM-powered ReAct SQL Agent** that answers business queries from a **sales dataset** stored in a SQL database.
Users can interact with the bot through a **Streamlit-based UI**, where natural language questions are converted into SQL queries, executed against the database, and then summarized into **executive-level insights**.

The agent follows the **ReAct framework** (Reasoning + Acting) with multiple tools:

1. **SQL Generator** – Converts user queries into SQL statements.
2. **SQL Executor** – Runs queries against the database.
3. **Business Summary Generator** – Produces concise insights for decision-makers.

---

## ⚙️ Tech Stack

* **Python** (3.12+)
* **LangChain** – Agent orchestration (ReAct framework)
* **Groq API (LLM)** – Using `llama-3.1-8b-instant` for SQL generation & summarization
* **SQLAlchemy + PyMySQL** – Database connection layer
* **Pandas** – SQL results handling
* **Streamlit** – Web-based chatbot UI
* **MySQL / SQLite** – Backend database (sales data)

---

## 🚀 How to Run the Bot

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/react-sql-agent.git
cd react-sql-agent
```

### 2️⃣ Setup Virtual Environment
#### Code Base
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```
#### Data Preparation
##### Setup of SQL
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y mysql-server mysql-client
sudo systemctl enable --now mysql
```
##### Setup of SQL
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y mysql-server mysql-client
sudo systemctl enable --now mysql
```

#### Create DB
```bash
CREATE DATABASE rpsg_rag;
CREATE USER 'rpsg_user'@'localhost' IDENTIFIED BY 'RPSG_rag1';
GRANT ALL PRIVILEGES ON rpsg_rag.* TO 'rpsg_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

### 3️⃣ Install Dependencies

```bash
pip install -r requirement.txt
```

### 4️⃣ Setup Environment Variables

Create a `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=salesdb
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

Add The following two lines in `react_agent.py` file:
```bash
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") #("Your DB Password")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") #("Your GROQ API Key")
```
### 5️⃣ Run Locally

#### Load Data
Place /data folder in the root folder then run the following commands:

```bash
python3 create_db.py
python3 load_data.py
```
#### Start Application
```bash
streamlit run react_app.py
```

### 6️⃣ Deployment on Streamlit Cloud

* Push code + `requirement.txt` + `.env.example` to GitHub
* Add environment variables in Streamlit Cloud dashboard
* Deploy and get a public URL 🎉

---

## 🛠️ Design Decisions

1. **Why ReAct and not LangGraph?**

   * ReAct provides a **lightweight, modular agent design** with tool-based reasoning steps.
   * LangGraph is powerful for **multi-agent, stateful workflows**, but for a **single-agent SQL retrieval pipeline**, ReAct is simpler and more transparent.

2. **Why `llama-3.1-8b-instant` over larger models (like `70b`)?**

   * **Low latency**: 8B runs significantly faster for SQL generation tasks.
   * **Cost efficiency**: Using a smaller model reduces API costs.
   * **Performance**: For structured SQL + summarization, `8b-instant` provides sufficient accuracy.
   * Larger models (`70b`, GPT-OSS) could be explored if queries become more complex or multi-table joins are introduced.

---

## 🔮 Future Steps

* **SQL Indexing** → Optimize queries by adding proper indexes to reduce query latency.
* **Query Caching (24h TTL)** → Cache common queries/responses to **reduce cost and response time**.
* **Improved Guardrails** → Add filters to prevent exposure of **PII or sensitive financial data**.
* **Multi-table Support** → Extend SQL agent to handle joins across multiple sales-related tables.
* **Analytics Dashboard** → Integrate more visualization (charts/plots) in Streamlit for richer insights.

---

## 📌 Example Queries

* "What are the monthly sales across Channel 1 since Jan 2025?"
* "What is the share of units sold across various channels since Jan 2025?"
* "Tell me the top 5 days with the highest daily units sold?"

---
