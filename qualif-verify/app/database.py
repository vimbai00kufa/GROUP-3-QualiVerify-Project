"""Database engine and declarative base (SQLAlchemy 2.x)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def make_engine(database_url: str):
    """Create a SQLAlchemy engine for the given database URL."""
    connect_args = {}
    pool_kwargs = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        pool_kwargs["poolclass"] = NullPool
    return create_engine(database_url, connect_args=connect_args, **pool_kwargs)


def make_session_factory() -> sessionmaker:
    """Create a session factory (bound to an engine at request time)."""
    return sessionmaker(autocommit=False, autoflush=False)
