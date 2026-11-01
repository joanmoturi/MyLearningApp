"""Extend validated personal envelopes without deleting existing learning data."""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

OLD = "kind IN ('note','resource','competency','company','job','project','attempt','review','settings')"
NEW = OLD[:-1] + ",'coding_session')"


def upgrade():
    with op.batch_alter_table(
        "personal_records", naming_convention={"ck": "ck_%(table_name)s_kind"}
    ) as batch:
        batch.drop_constraint("ck_personal_records_kind", type_="check")
        batch.create_check_constraint("ck_personal_records_kind", NEW)


def downgrade():
    raise RuntimeError("Export coding sessions before a separately reviewed downgrade; no data is deleted.")
