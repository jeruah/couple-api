from sqlalchemy import NullPool
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os


os.makedirs("./database", exist_ok=True)
load_dotenv()
# Allow overriding the database URL via an environment variable so tests can use
# a temporary database file.
USER = os.getenv("user")

if USER:
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    DATABASE_URL = "sqlite:///./database/sql_app.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )


def get_db():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")