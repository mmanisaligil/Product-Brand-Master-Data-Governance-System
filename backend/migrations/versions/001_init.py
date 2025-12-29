"""init schema

Revision ID: 001_init
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "skus",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("brand", sa.String(), nullable=False),
        sa.Column("canonical_name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_skus_status", "skus", ["status"])

    op.create_table(
        "sku_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("alias_type", sa.String(), nullable=False),
        sa.Column("alias_value", sa.String(), nullable=False),
    )
    op.create_index("ix_sku_aliases_value", "sku_aliases", ["alias_value"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("issuer", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("file_hash", sa.String(), nullable=False),
        sa.Column("reliability_score", sa.Float(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("page_section", sa.String(), nullable=True),
    )
    op.create_index("ix_evidence_hash", "evidence", ["file_hash"])

    op.create_table(
        "field_values",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("needs_review", sa.Boolean(), server_default=sa.text("false")),
    )
    op.create_index("ix_field_values_sku", "field_values", ["sku_id"])

    op.create_table(
        "er_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("match_explanation", sa.Text(), nullable=False),
        sa.Column("decision_source", sa.String(), nullable=False),
        sa.Column("needs_review", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("locked", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "conflict_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("resolution", sa.String(), nullable=False),
        sa.Column("chosen_field_value_id", sa.Integer(), sa.ForeignKey("field_values.id"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "change_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("evidence_id", sa.String(), sa.ForeignKey("evidence.id"), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("old_value", sa.String(), nullable=True),
        sa.Column("new_value", sa.String(), nullable=True),
        sa.Column("diff_note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("export_version", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("exports")
    op.drop_table("change_logs")
    op.drop_table("conflict_logs")
    op.drop_table("er_decisions")
    op.drop_index("ix_field_values_sku", table_name="field_values")
    op.drop_table("field_values")
    op.drop_index("ix_evidence_hash", table_name="evidence")
    op.drop_table("evidence")
    op.drop_index("ix_sku_aliases_value", table_name="sku_aliases")
    op.drop_table("sku_aliases")
    op.drop_index("ix_skus_status", table_name="skus")
    op.drop_table("skus")
