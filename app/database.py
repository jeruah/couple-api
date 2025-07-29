from sqlmodel import create_engine, Session, SQLModel
import os


os.makedirs("./database", exist_ok=True)

SQLMODEL_DATABASE_URL = "sqlite:///./database/sql_app.db"

engine = create_engine(
    SQLMODEL_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

def get_db():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)