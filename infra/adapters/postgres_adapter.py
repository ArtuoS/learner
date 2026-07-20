import os

import psycopg2
import psycopg2.extras

from infra.ports.database import Database


class PostgresAdapter(Database):

    def __init__(self) -> None:
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY,
                    message_from VARCHAR(10) NOT NULL CHECK (message_from IN ('user', 'system')),
                    content TEXT NOT NULL,
                    tenant_id UUID NOT NULL,
                    session_id UUID,
                    created_at TIMESTAMP DEFAULT NOW(),
                    model VARCHAR(255)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id UUID PRIMARY KEY,
                    tenant_id UUID NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    tenant_id UUID NOT NULL,
                    size BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()

    def execute(self, query: str, params: tuple = ()) -> list[dict]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            self.conn.commit()
            return []
