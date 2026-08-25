"""initial migration for role, user, tender, tenderstatushistory

Revision ID: initial_migration_001
Revises:
Create Date: 2026-08-23 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = "initial_migration_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Table Role
    op.create_table(
        "Role",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Role_id"), "Role", ["id"], unique=False)

    # Table User
    op.create_table(
        "User",
        sa.Column("first_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("last_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("birthdate", sa.DateTime(timezone=True), nullable=True),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("gender", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("country", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("role_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["Role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_User_email"), "User", ["email"], unique=True)
    op.create_index(op.f("ix_User_id"), "User", ["id"], unique=False)
    op.create_index(
        op.f("ix_User_hashed_password"), "User", ["hashed_password"], unique=False
    )

    # Table Tender
    op.create_table(
        "Tender",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["User.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Tender_id"), "Tender", ["id"], unique=False)
    op.create_index(op.f("ix_Tender_title"), "Tender", ["title"], unique=False)
    op.create_index(op.f("ix_Tender_status"), "Tender", ["status"], unique=False)

    # Table TenderStatusHistory
    op.create_table(
        "TenderStatusHistory",
        sa.Column("tender_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("old_status", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("new_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("changed_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tender_id"],
            ["Tender.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_id"],
            ["User.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_TenderStatusHistory_id"), "TenderStatusHistory", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_TenderStatusHistory_tender_id"),
        "TenderStatusHistory",
        ["tender_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_TenderStatusHistory_tender_id"), table_name="TenderStatusHistory"
    )
    op.drop_index(op.f("ix_TenderStatusHistory_id"), table_name="TenderStatusHistory")
    op.drop_table("TenderStatusHistory")
    op.drop_index(op.f("ix_Tender_status"), table_name="Tender")
    op.drop_index(op.f("ix_Tender_title"), table_name="Tender")
    op.drop_index(op.f("ix_Tender_id"), table_name="Tender")
    op.drop_table("Tender")
    op.drop_index(op.f("ix_User_hashed_password"), table_name="User")
    op.drop_index(op.f("ix_User_id"), table_name="User")
    op.drop_index(op.f("ix_User_email"), table_name="User")
    op.drop_table("User")
    op.drop_index(op.f("ix_Role_id"), table_name="Role")
    op.drop_table("Role")
