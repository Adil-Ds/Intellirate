"""Add user_rate_limit_configs table

Revision ID: 002_user_rate_limits
Revises: 001_request_logs
Create Date: 2025-12-29 10:58:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '002_user_rate_limits'
down_revision = '001_request_logs'
branch_labels = None
depends_on = None


def upgrade():
    """Create user_rate_limit_configs table"""
    op.create_table(
        'user_rate_limit_configs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        
        # User Information
        sa.Column('user_id', sa.String(length=255), nullable=False, unique=True),
        
        # Rate Limit Configuration
        sa.Column('tier', sa.String(length=50), nullable=False),
        sa.Column('custom_limit', sa.Integer(), nullable=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    
    # Create index for better query performance
    op.create_index('idx_user_rate_limit_user_id', 'user_rate_limit_configs', ['user_id'])


def downgrade():
    """Drop user_rate_limit_configs table"""
    op.drop_index('idx_user_rate_limit_user_id', table_name='user_rate_limit_configs')
    op.drop_table('user_rate_limit_configs')
