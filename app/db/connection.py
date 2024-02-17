from sqlmodel import create_engine, SQLModel

sqlite_db="youtube_t.db"

sqlite_url = f"sqlite:///{sqlite_db}"

engine=create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)