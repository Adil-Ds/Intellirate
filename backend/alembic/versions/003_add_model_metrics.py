"""Create model_metrics table

Revision ID: 003
Revises: 002
Create Date: 2025-12-29 13:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'model_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('metrics_json', JSON, nullable=False),
        sa.Column('trained_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_metrics_id'), 'model_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_model_metrics_model_name'), 'model_metrics', ['model_name'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_model_metrics_model_name'), table_name='model_metrics')
    op.drop_index(op.f('ix_model_metrics_id'), table_name='model_metrics')
    op.drop_table('model_metrics')
