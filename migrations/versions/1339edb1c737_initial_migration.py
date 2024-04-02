"""Initial migration

Revision ID: 1339edb1c737
Revises: 
Create Date: 2024-03-28 22:33:01.636038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1339edb1c737'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_post_timestamp'), ['timestamp'], unique=False)
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_post_timestamp'))
        batch_op.drop_column('timestamp')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###