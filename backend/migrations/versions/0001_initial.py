"""Initial local-first schema; domain envelopes are validated at API boundaries."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
    )
    op.create_table(
        "research_documents",
        sa.Column("name", sa.String(150), primary_key=True),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
    )
    op.create_table(
        "research_records",
        sa.Column("id", sa.String(150), primary_key=True),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("document_name", sa.String(150), sa.ForeignKey("research_documents.name"), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
    )
    op.create_index("ix_research_records_kind", "research_records", ["kind"])
    op.create_table(
        "plans",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("user_id", sa.String(100), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("track_id", sa.String(150), sa.ForeignKey("research_records.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_plans_user_id", "plans", ["user_id"])
    op.create_table(
        "plan_lessons",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("plan_id", sa.String(100), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("research_id", sa.String(150), sa.ForeignKey("research_records.id")),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("skipped", sa.Boolean(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.UniqueConstraint("plan_id", "sequence"),
        sa.CheckConstraint("day >= 1"),
    )
    op.create_index("ix_plan_lessons_plan_id", "plan_lessons", ["plan_id"])
    op.create_table(
        "progress",
        sa.Column(
            "slot_id", sa.String(100), sa.ForeignKey("plan_lessons.id", ondelete="CASCADE"), primary_key=True
        ),
        *(
            sa.Column(key, sa.Boolean(), nullable=False)
            for key in ("video", "reading", "practical", "knowledge")
        ),
        sa.Column("watched_minutes", sa.Integer(), nullable=False),
        sa.Column("study_minutes", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("watched_minutes >= 0 AND watched_minutes <= 1440"),
        sa.CheckConstraint("study_minutes >= 0 AND study_minutes <= 1440"),
    )
    op.create_table(
        "personal_records",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("user_id", sa.String(100), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("ref_key", sa.String(150)),
        sa.Column("research_ref", sa.String(150), sa.ForeignKey("research_records.id")),
        sa.Column("parent_id", sa.String(100), sa.ForeignKey("personal_records.id")),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "kind", "ref_key"),
        sa.CheckConstraint(
            "kind IN ('note','resource','competency','company','job','project','attempt','review','settings')"
        ),
    )
    op.create_index("ix_personal_records_user_id", "personal_records", ["user_id"])
    op.create_index("ix_personal_records_kind", "personal_records", ["kind"])
    op.create_table(
        "study_activity",
        sa.Column(
            "slot_id", sa.String(100), sa.ForeignKey("progress.slot_id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("day", sa.String(10), primary_key=True),
        sa.Column("minutes", sa.Integer(), nullable=False),
    )
    op.create_table(
        "import_previews",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("user_id", sa.String(100), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False),
        sa.Column("applied", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    for table in (
        "import_previews",
        "study_activity",
        "personal_records",
        "progress",
        "plan_lessons",
        "plans",
        "research_records",
        "research_documents",
        "users",
    ):
        op.drop_table(table)
