from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e486c2006bb1'
down_revision = '019cd21d88ef'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('business_users', schema=None) as batch_op:
        # Step 1: Add column with default value for existing rows
        batch_op.add_column(
            sa.Column('role', sa.String(length=50), nullable=True, server_default='customer')
        )
        # Step 2: Make column NOT NULL and remove default
        batch_op.alter_column('role', nullable=False, server_default=None)

def downgrade():
    with op.batch_alter_table('business_users', schema=None) as batch_op:
        batch_op.drop_column('role')