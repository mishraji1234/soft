from datetime import datetime
from app import db
from sqlalchemy import event

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)  # Changed from 'type' to 'account_type'
    balance = db.Column(db.Numeric(15, 2), default=0)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    debit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    credit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    reference_type = db.Column(db.String(20))  # invoice/voucher
    reference_id = db.Column(db.Integer)
    
    # Foreign key to Invoice model
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    
    # Foreign key to Voucher model
    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'))
    
    debit_account = db.relationship('Account', foreign_keys=[debit_account_id])
    credit_account = db.relationship('Account', foreign_keys=[credit_account_id])

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # sale/purchase
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='draft')  # draft/posted/paid

    # Relationship to JournalEntry model
    journal_entries = db.relationship('JournalEntry', backref='invoice')

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payee = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # payment/receipt
    status = db.Column(db.String(20), default='draft')  # draft/posted

    # Relationship to JournalEntry model
    journal_entries = db.relationship('JournalEntry', backref='voucher')

# Automatic Journal Entry Creation
@event.listens_for(Invoice, 'after_update')
def create_invoice_journal(mapper, connection, target):
    if target.status == 'posted' and not target.journal_entries:
        if target.type == 'sale':
            debit_account = 'Accounts Receivable'
            credit_account = 'Sales Revenue'
        else:
            debit_account = 'Inventory'
            credit_account = 'Accounts Payable'
        
        db.session.add(JournalEntry(
            date=target.date,
            debit_account_id=Account.query.filter_by(name=debit_account).first().id,
            credit_account_id=Account.query.filter_by(name=credit_account).first().id,
            amount=target.total_amount,
            description=f"Invoice {target.number}",
            reference_type='invoice',
            reference_id=target.id,
            invoice_id=target.id  # Set the invoice_id foreign key
        ))

@event.listens_for(Voucher, 'after_update')
def create_voucher_journal(mapper, connection, target):
    if target.status == 'posted' and not target.journal_entries:
        if target.type == 'payment':
            debit_account = 'Expense Account'
            credit_account = 'Cash'
        else:
            debit_account = 'Cash'
            credit_account = 'Income Account'
        
        db.session.add(JournalEntry(
            date=target.date,
            debit_account_id=Account.query.filter_by(name=debit_account).first().id,
            credit_account_id=Account.query.filter_by(name=credit_account).first().id,
            amount=target.amount,
            description=f"Voucher {target.number}",
            reference_type='voucher',
            reference_id=target.id,
            voucher_id=target.id  # Set the voucher_id foreign key
        ))