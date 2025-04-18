"""Initial tables

Revision ID: 855c816daf54
Revises: 
Create Date: 2025-03-31 01:16:34.143503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '855c816daf54'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('account_type', sa.String(length=50), nullable=True),
    sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('journal_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('reference', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('source_type', sa.String(length=20), nullable=True),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('is_posted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('customer_name', sa.String(length=100), nullable=False),
    sa.Column('tin_id', sa.String(length=50), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('dr_cr', sa.String(length=2), nullable=True),
    sa.Column('account_type', sa.String(length=20), nullable=True),
    sa.Column('account_no', sa.String(length=20), nullable=True),
    sa.Column('sub_account', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('base_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('vat', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('withholding_tax', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('journal_entry_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('journal_entry_line',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('journal_id', sa.Integer(), nullable=True),
    sa.Column('debit_account_id', sa.Integer(), nullable=True),
    sa.Column('credit_account_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('vat_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('withholding_tax_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['credit_account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['debit_account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['journal_id'], ['journal_entry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('voucher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('voucher_number', sa.String(length=20), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('id_number', sa.String(length=50), nullable=True),
    sa.Column('tin_number', sa.String(length=50), nullable=True),
    sa.Column('voucher_type', sa.String(length=20), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('vat', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('withhold_tax', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('account_type', sa.String(length=20), nullable=True),
    sa.Column('journal_entry_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entry.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('voucher_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('voucher')
    op.drop_table('journal_entry_line')
    op.drop_table('invoice')
    op.drop_table('journal_entry')
    op.drop_table('account')
    # ### end Alembic commands ###
