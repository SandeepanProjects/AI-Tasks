from __future__ import annotations

import os
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver


def create_database_resources():
    database_url = os.environ["DATABASE_URL"]
    pool = ConnectionPool(
        conninfo=database_url,
        min_size=int(os.getenv("DB_POOL_MIN_SIZE", "1")),
        max_size=int(os.getenv("DB_POOL_MAX_SIZE", "10")),
        timeout=10,
        kwargs={"autocommit": True, "row_factory": dict_row},
        open=False,
    )
    pool.open(wait=True)
    checkpointer = PostgresSaver(pool)

    # For a simple single-instance demo. In production, run this as a
    # controlled migration/deployment job, not concurrently from every replica.
    if os.getenv("RUN_CHECKPOINT_SETUP", "false").lower() == "true":
        checkpointer.setup()

    with pool.connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_ownership (
                thread_id UUID PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_approval_audit (
                id BIGSERIAL PRIMARY KEY,
                thread_id UUID NOT NULL,
                tenant_id TEXT NOT NULL,
                approval_id TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                decision TEXT NOT NULL CHECK (decision IN ('approve', 'reject')),
                comment TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (thread_id, approval_id)
            )
        """)
    return pool, checkpointer


def register_workflow(pool: ConnectionPool, thread_id: str, tenant_id: str) -> None:
    with pool.connection() as conn:
        conn.execute(
            "INSERT INTO workflow_ownership(thread_id, tenant_id) VALUES (%s, %s)",
            (thread_id, tenant_id),
        )


def verify_ownership(pool: ConnectionPool, thread_id: str, tenant_id: str) -> bool:
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM workflow_ownership WHERE thread_id = %s AND tenant_id = %s",
            (thread_id, tenant_id),
        ).fetchone()
    return row is not None


def get_approval_audit(pool: ConnectionPool, thread_id: str, approval_id: str):
    with pool.connection() as conn:
        return conn.execute(
            """SELECT decision, reviewer_id, comment
               FROM workflow_approval_audit
               WHERE thread_id = %s AND approval_id = %s""",
            (thread_id, approval_id),
        ).fetchone()


def record_approval(pool: ConnectionPool, *, thread_id: str, tenant_id: str,
                    approval_id: str, reviewer_id: str, decision: str,
                    comment: str | None) -> bool:
    """Persist an approval decision. Returns False if this approval_id already exists."""
    with pool.connection() as conn:
        row = conn.execute(
            """INSERT INTO workflow_approval_audit
               (thread_id, tenant_id, approval_id, reviewer_id, decision, comment)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (thread_id, approval_id) DO NOTHING
               RETURNING id""",
            (thread_id, tenant_id, approval_id, reviewer_id, decision, comment),
        ).fetchone()
    return row is not None
