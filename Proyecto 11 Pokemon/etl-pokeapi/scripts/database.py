#!/usr/bin/env python3
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

def _get_db_config():
    # Intento 1: st.secrets (Streamlit Cloud)
    try:
        import streamlit as st
        host = st.secrets.get("DB_HOST", "")
        if host and host != "localhost":
            return {
                "host":     host,
                "port":     st.secrets.get("DB_PORT", "5432"),
                "user":     st.secrets.get("DB_USER", "postgres"),
                "password": st.secrets.get("DB_PASSWORD", ""),
                "dbname":   st.secrets.get("DB_NAME", "postgres"),
            }
    except Exception:
        pass  # st no disponible en scripts locales

    # Intento 2: .env (desarrollo local)
    from dotenv import load_dotenv
    load_dotenv()
    return {
        "host":     os.getenv("DB_HOST", "localhost"),
        "port":     os.getenv("DB_PORT", "5432"),
        "user":     os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "dbname":   os.getenv("DB_NAME", "pokeapi_etl"),
    }

cfg = _get_db_config()

DATABASE_URL = (
    f"postgresql://{quote_plus(cfg['user'])}:{quote_plus(cfg['password'])}"
    f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}?sslmode=require"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {str(e)}")
        return False