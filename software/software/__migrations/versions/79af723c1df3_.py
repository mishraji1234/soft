"""empty message

Revision ID: 79af723c1df3
Revises: 855c816daf54
Create Date: 2025-04-03 09:30:06.937740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79af723c1df3'
down_revision = '855c816daf54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invoice')
    op.drop_table('journal_entry')
    op.drop_table('voucher')
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_posted', sa.Boolean(), nullable=True))

    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('journal_entry_id')

    with op.batch_alter_table('journal_entry_line', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'journal_entries', ['journal_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('journal_entry_line', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'journal_entry', ['journal_id'], ['id'])

    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('journal_entry_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(None, 'journal_entries', ['journal_entry_id'], ['id'])

    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('is_posted')

    op.create_table('voucher',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('voucher_number', sa.VARCHAR(length=20), nullable=True),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('id_number', sa.VARCHAR(length=50), nullable=True),
    sa.Column('tin_number', sa.VARCHAR(length=50), nullable=True),
    sa.Column('voucher_type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('total_amount', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('vat', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('withhold_tax', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('account_type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('journal_entry_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entry.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('voucher_number')
    )
    op.create_table('journal_entry',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('reference', sa.VARCHAR(length=50), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('source_type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('source_id', sa.INTEGER(), nullable=True),
    sa.Column('is_posted', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=True),
    sa.Column('customer_name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('tin_id', sa.VARCHAR(length=50), nullable=True),
    sa.Column('type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('dr_cr', sa.VARCHAR(length=2), nullable=True),
    sa.Column('account_type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('account_no', sa.VARCHAR(length=20), nullable=True),
    sa.Column('sub_account', sa.VARCHAR(length=50), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('base_amount', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('vat', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('withholding_tax', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('total_amount', sa.NUMERIC(precision=15, scale=2), nullable=True),
    sa.Column('journal_entry_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
