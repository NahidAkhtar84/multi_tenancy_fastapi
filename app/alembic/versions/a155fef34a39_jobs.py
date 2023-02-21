"""jobs

Revision ID: a155fef34a39
Revises: fe69bd1396dc
Create Date: 2023-02-21 14:02:43.161363

"""
from alembic import op
import sqlalchemy as sa


from app.alembic.tenant import for_each_tenant_schema

# revision identifiers, used by Alembic.
revision = 'a155fef34a39'
down_revision = 'fe69bd1396dc'
branch_labels = None
depends_on = None

def upgrade() -> None:

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    )
    op.create_index(op.f('ix_tenant_default_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_tenant_default_users_full_name'), 'users', ['full_name'], unique=False)
    op.create_index(op.f('ix_tenant_default_users_id'), 'users', ['id'], unique=False)

    op.create_table('jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_jobs')),
    )
    op.create_index(op.f('ix_tenant_default_jobs_id'), 'jobs', ['id'], unique=False)
   
    # ### end Alembic commands ###


def downgrade() -> None:
  
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tenant_default_users_id'), table_name='users')
    op.drop_index(op.f('ix_tenant_default_users_full_name'), table_name='users')
    op.drop_index(op.f('ix_tenant_default_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_tenant_default_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    # ### end Alembic commands ###
