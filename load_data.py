# load_data.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "rpsg_rag")
MYSQL_USER = os.getenv("MYSQL_USER", "rpsg_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "RPSG_rag1")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL)

def load_excel_to_mysql(file_path, table_name="sales_data", if_exists="append"):
    print(f"📂 Loading {file_path} -> {table_name}")
    df = pd.read_excel(file_path)

    # Standardize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    # Load into MySQL
    df.to_sql(table_name, engine, index=False, if_exists=if_exists)
    print(f"✅ Loaded {len(df)} rows into {table_name}")

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "data", "Assignment 1 - Sample Data.xlsx")
    load_excel_to_mysql(file_path)
