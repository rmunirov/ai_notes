"""agent thread / message tables

Revision ID: 003
Revises: 002
Create Date: 2026-04-26

"""

from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE agent_threads (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        """
        CREATE TABLE agent_messages (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            thread_id uuid NOT NULL REFERENCES agent_threads(id) ON DELETE CASCADE,
            role text NOT NULL CHECK (role IN ('user', 'assistant')),
            content text NOT NULL,
            source_note_ids uuid[] NOT NULL DEFAULT '{}',
            confidence_level text CHECK (confidence_level IS NULL OR
                confidence_level IN ('high', 'medium', 'low', 'none')),
            created_at timestamptz NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX agent_messages_thread_idx ON agent_messages (thread_id, created_at);"
    )
    op.execute(
        """
        CREATE TRIGGER agent_threads_updated_at
        BEFORE UPDATE ON agent_threads
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS agent_messages;")
    op.execute("DROP TRIGGER IF EXISTS agent_threads_updated_at ON agent_threads;")
    op.execute("DROP TABLE IF EXISTS agent_threads;")
