"""Add users, contact ownership, and birthday date type.

Revision ID: 002
Revises: 001
Create Date: 2026-05-24 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.add_column("contacts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.alter_column(
        "contacts",
        "birthday",
        existing_type=sa.String(length=10),
        type_=sa.Date(),
        postgresql_using="TO_DATE(birthday, 'YYYY-MM-DD')",
        nullable=False,
    )

    connection = op.get_bind()
    legacy_user_id = connection.execute(
        sa.text(
            """
            INSERT INTO users (username, email, hashed_password, is_verified)
            VALUES (:username, :email, :hashed_password, true)
            ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
            """
        ),
        {
            "username": "legacy",
            "email": "legacy@local.invalid",
            "hashed_password": "legacy-user-no-login",
        },
    ).scalar_one()

    connection.execute(
        sa.text("UPDATE contacts SET user_id = :user_id WHERE user_id IS NULL"),
        {"user_id": legacy_user_id},
    )

    op.alter_column("contacts", "user_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_contacts_user_id_users",
        "contacts",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_contacts_user_id_users", "contacts", type_="foreignkey")
    op.drop_column("contacts", "user_id")
    op.alter_column(
        "contacts",
        "birthday",
        existing_type=sa.Date(),
        type_=sa.String(length=10),
        postgresql_using="TO_CHAR(birthday, 'YYYY-MM-DD')",
        nullable=False,
    )
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")