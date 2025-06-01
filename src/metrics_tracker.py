import os
import sqlite3
from datetime import datetime
import Levenshtein  

DB_PATH = os.path.join(os.path.dirname(__file__), "performance_metrics.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                llm_name TEXT,
                nl_query TEXT,
                generated_sql TEXT,
                expected_sql TEXT,
                exact_match INTEGER,
                levenshtein_distance REAL,
                semantic_match INTEGER,
                latency REAL
            )
        """)

def record_metrics(llm_name, nl_query, generated_sql, expected_sql, result_match, latency):
    exact_match = int(generated_sql.strip().lower() == expected_sql.strip().lower())
    levenshtein = Levenshtein.distance(generated_sql.strip(), expected_sql.strip())
    semantic_match = int(result_match)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO evaluation (
                timestamp, llm_name, nl_query, generated_sql, expected_sql,
                exact_match, levenshtein_distance, semantic_match, latency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(), llm_name, nl_query, generated_sql, expected_sql,
            exact_match, levenshtein, semantic_match, latency
        ))
def get_recent_metrics(limit=50):
    import pandas as pd
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM evaluation ORDER BY timestamp DESC LIMIT {limit}", conn
        )
    return df
