# react_sql_agent.py
import pymysql
import pandas as pd
from langchain.agents import create_react_agent, Tool, AgentExecutor
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()
# -------------------------
# DB Utilities
# -------------------------


MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "rpsg_rag")
MYSQL_USER = os.getenv("MYSQL_USER", "rpsg_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") #("Your DB Password")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") #("Your GROQ API Key")

def get_connection():
    """Create and return a SQLAlchemy engine for MySQL."""
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    return engine

def run_sql_query(query: str):
    """Execute SQL query and return result as pandas DataFrame."""
    # Strip outer quotes if LLM returns a quoted string
    query = query.strip().strip('"').strip("'")
    engine = get_connection()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
    except Exception as e:
        raise e
    finally:
        engine.dispose()
    return df


# -------------------------
# LLM Setup (Groq)
# -------------------------
llm = ChatGroq(
    model= "llama-3.1-8b-instant",
    #"meta-llama/llama-guard-4-12b", #"llama-3.3-70b-versatile", #"llama-3.1-8b-instant", #"mixtral-8x7b-32768",  # or llama2-70b-4096
    temperature=0,
    api_key=GROQ_API_KEY
)

# -------------------------
# Tools
# -------------------------
def domain_check_tool(query: str) -> str:
    if any(word in query.lower() for word in ["sales", "product", "channel", "city", "quantity", "units"]):
        return "related"
    return "not related to Data"

def sql_generator_tool(query: str) -> str:
    prompt = f"""
    You are a SQL generator.
    Table: sales_data (columns: Date (date type), Channel(string), Product_Name(string), City(string), Quantity(integer), Sales(float)).
    User query: "{query}"
    Write a valid MySQL query:
    Note: Try to Keep the sql query as simple as possible don't make it complex.
    """
    resp = llm.invoke(prompt)
    return resp.content.strip()

def sql_executor_tool(sql: str) -> str:

    try:
        df = run_sql_query(sql)
        return df.head(10).to_json(orient="records")
    except Exception as e:
        return f"SQL Error: {e}"

def summary_tool(results: str) -> str:
    prompt = f"""
    You are a business analyst. 
    Summarize the following SQL results in 2-3 executive-friendly sentences.
    Results: {results}
    """
    resp = llm.invoke(prompt)
    return resp.content.strip()

# Wrap tools
tools = [
    Tool(name="DomainCheck", func=domain_check_tool, description="Check if query is about sales data"),
    Tool(name="SQLGenerator", func=sql_generator_tool, description="Generate SQL query for sales_data table"),
    Tool(name="SQLExecutor", func=sql_executor_tool, description="Execute SQL query and return rows"),
    Tool(name="Summary", func=summary_tool, description="Summarize SQL results in business language")
]

# -------------------------
# Custom ReAct Prompt
# -------------------------
react_prompt = PromptTemplate.from_template("""
You are a ReAct agent that answers business questions using sales_data.

You have access to the following tools:
{tools}

When you decide to use a tool, you must use the exact name from this list:
{tool_names}

Follow this process strictly:
1. First ensure the query is relevant to sales.
    Thought: I need to ensure the query is relevant to sales.
    Action: DomainCheck tool to check relevane of the query to the present data
    Action Input: <User Query>
    Sample: "Tell me the top 5 days with the highest daily units sold?"
   - Check if the query is related to sales_data (monthly sales, products, cities, channels, units, etc.).
   - If it is unrelated (like about weather, cricket, movies, politics, economic, art, science etc.), respond ONLY with: "not related to Sales Data".
   Observation: "What are the monthly sales across Channel 1 since Jan 2025?"

2. If related to Sales Data, use SQLGenerator to create a SQL query.
    Thought: I need to generate the SQL First.
    Action: SQLGenerator tool to generate SQL
    Action Input: <User Query>
    Sample: "Tell me the top 5 days with the highest daily units sold?"
    Observation: SELECT ... (SQL Generated)

3. Pass the SQL to SQLExecutor to run it.
    Thought: I will execute the SQL Query
    Action: SQLExecutor tool to execute SQL Query
    Action Input: "SELECT ..."
    - If SQLExecutor returns "SQL Error", 
    Observation: Dataframe fetched from sales_data table based on the given query.
    
    

4. Once valid results are obtained, pass them to Summary. This is the **Final Step**
    Thought: Now based on the dataframe I will prepare a summary as a business analyst. Key points will be highlighted as bullet points and focus will be on Focus on trends, comparisons.
    Action: Summary tool to generate the Natural Response
    Action Input: Dataframe from SQLExecutor
    Observation: Business Summary as Natural Response (The Final Output)
    Note: End the work of React Agent Here.

**Guardrails**:
    1. If the user query is not related to sales_data table then do not try to generate any sql query terminate with a reply: "not related to Sales Data"
    2. Note: The output of SQL Query will be a dataframe.
    3. Try to generate the final summary related to the SQL results and numbers do not make it complex or long.
    4. Do not follow the example/sample query or output format focus on the input Query given by the User and generate results Accordingly.
    5. Stick to the User Query given, do not pick or assume any other or old query from memory.
    6. Pick the tool from the given tool list do not try to improvise new tool
    7. After Step4 Once the Summary is generated do not run the Thought Action Loop again. End the Chain there and return the Final Response.

Final Answer: <summary or not related message>

Begin!

{agent_scratchpad}

""")

"""
Use the format:
Thought: <your reasoning>
Action: <tool name> (if tool is needed to use) regenerate SQL and try again (max 3 attempts).
Action Input: <input>
Observation: <tool output>
... (repeat)

"""

"""
Note: "What are the monthly sales across Channel 1 since Jan 2025?"**(this is an example/sample user query format)**
Note: **this is an example/sample user query output format**
    +---------------+---------+-----------+
    | monthly_sales | month   | Channel   |
    +---------------+---------+-----------+
    |    1959149285 | 2025-01 | Channel 1 |
    |    1705501202 | 2025-02 | Channel 1 |
    |    1839695521 | 2025-03 | Channel 1 |
    +---------------+---------+-----------+
"""

# -------------------------
# Create ReAct Agent
# -------------------------
react_agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)
agent_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True,handle_parsing_errors=True)

# -------------------------
# Example Run
# -------------------------
if __name__ == "__main__":
    queries = [
        #"What are the monthly sales across Channel 1 since Jan 2025?",
        #"What is the share of units sold across various channels since Jan 2025?",
        "Tell me the top 5 days with the highest daily units sold?",
        #"Who won the cricket world cup in 2023?"
    ]

    for q in queries:
        print("\n🔍 Query:", q)
        response = agent_executor.invoke({"input": q})
        print("🤖 Final Response:", response)

#SELECT SUM(Quantity) AS monthly_sales, DATE_FORMAT(Date, '%Y-%m') AS month, Channel FROM sales_data WHERE Channel = 'Channel 1' AND Date >= '2025-01-01' GROUP BY DATE_FORMAT(Date, '%Y-%m'), Channel ORDER BY month;