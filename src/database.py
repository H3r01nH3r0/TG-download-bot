from .settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

Session = sessionmaker(
    engine,
    autoflush=False,
    autocommit=False
)
