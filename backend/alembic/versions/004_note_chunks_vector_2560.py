"""note_chunks: vector(1536) -> vector(2560)

Old embeddings are cleared (must re-run full reindex).

Revision ID: 004
Revises: 003
Create Date: 2026-04-26

"""

from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector: ivfflat (and classic HNSW) cap at 2000 dims, so 2560-d vectors have no ANN index.
    # Similarity search still works; large tables may need fewer dimensions or a different index strategy.
    op.execute("DROP INDEX IF EXISTS note_chunks_embedding_idx;")
    op.execute("UPDATE note_chunks SET embedding = NULL;")
    op.execute("ALTER TABLE note_chunks ALTER COLUMN embedding TYPE vector(2560);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS note_chunks_embedding_idx;")
    op.execute("UPDATE note_chunks SET embedding = NULL;")
    op.execute("ALTER TABLE note_chunks ALTER COLUMN embedding TYPE vector(1536);")
    op.execute(
        """
        CREATE INDEX note_chunks_embedding_idx
        ON note_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
    )
