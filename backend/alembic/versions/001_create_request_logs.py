"""Create request_logs table

Revision ID: 001_request_logs
Revises: 
Create Date: 2025-12-24 15:23:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '001_request_logs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create request_logs table for traffic capture"""
    op.create_table(
        'request_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('request_id', sa.String(length=255), nullable=False, unique=True),
        
        # User Information
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        
        # Timestamps
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Request Details
        sa.Column('endpoint', sa.String(length=100), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True, server_default='POST'),
        
        # AI Model Parameters
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        
        # Response Details
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        
        # Token Usage
        sa.Column('prompt_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, server_default='0'),
        
        # Performance Metrics
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('groq_latency_ms', sa.Integer(), nullable=True),
        
        # Metadata
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
    )
    
    # Create indexes for better query performance
    op.create_index('idx_user_id', 'request_logs', ['user_id'])
    op.create_index('idx_timestamp', 'request_logs', ['timestamp'])
    op.create_index('idx_request_id', 'request_logs', ['request_id'])
    op.create_index('idx_user_timestamp', 'request_logs', ['user_id', 'timestamp'])
    op.create_index('idx_success_timestamp', 'request_logs', ['success', 'timestamp'])


def downgrade():
    """Drop request_logs table"""
    op.drop_index('idx_success_timestamp', table_name='request_logs')
    op.drop_index('idx_user_timestamp', table_name='request_logs')
    op.drop_index('idx_request_id', table_name='request_logs')
    op.drop_index('idx_timestamp', table_name='request_logs')
    op.drop_index('idx_user_id', table_name='request_logs')
    op.drop_table('request_logs')
