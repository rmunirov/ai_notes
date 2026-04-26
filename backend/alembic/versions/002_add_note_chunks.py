"""add note_chunks with pgvector

Revision ID: 002
Revises: 001
Create Date: 2026-04-26

"""

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute(
        """
        CREATE TABLE note_chunks (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            note_id uuid NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            chunk_index integer NOT NULL,
            chunk_text text NOT NULL,
            embedding vector(1536),
            indexed_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_note_chunk UNIQUE (note_id, chunk_index)
        );
        """
    )
    op.execute(
        """
        CREATE INDEX note_chunks_embedding_idx
        ON note_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS note_chunks_embedding_idx;")
    op.execute("DROP TABLE IF EXISTS note_chunks;")
