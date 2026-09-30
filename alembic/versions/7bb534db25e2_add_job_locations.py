"""Allow jobs to have multiple locations.

Revision ID: 7bb534db25e2
Revises: 03b90628175b
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7bb534db25e2"
down_revision: str | Sequence[str] | None = "03b90628175b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_locations",
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"]),
        sa.PrimaryKeyConstraint("job_id", "location_id"),
    )
    op.execute(
        "INSERT INTO job_locations (job_id, location_id) "
        "SELECT id, location_id FROM jobs"
    )
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.drop_column("location_id")


def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.add_column(sa.Column("location_id", sa.Integer(), nullable=True))

    op.execute(
        "UPDATE jobs SET location_id = ("
        "SELECT MIN(location_id) FROM job_locations "
        "WHERE job_locations.job_id = jobs.id)"
    )

    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column("location_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_jobs_location_id_locations", "locations", ["location_id"], ["id"]
        )
    op.drop_table("job_locations")
