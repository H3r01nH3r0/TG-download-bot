from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, nullable=False)
    connection_name = sa.Column(sa.String, nullable=False)
    connection_file = sa.Column(sa.String, unique=True, nullable=False)
