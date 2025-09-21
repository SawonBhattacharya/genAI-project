# create_db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "rpsg_rag")
MYSQL_USER = os.getenv("MYSQL_USER", "rpsg_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "RPSG_rag1")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

Base = declarative_base()

class SalesData(Base):
    __tablename__ = "sales_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    channel = Column(String(128), nullable=False)
    product_name = Column(String(256), nullable=False)
    city = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False)
    sales = Column(Float, nullable=False)

def create_db_and_tables():
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully on", DATABASE_URL)

if __name__ == "__main__":
    create_db_and_tables()
