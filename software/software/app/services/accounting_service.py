from app.models.accounting import Invoice, Voucher, JournalEntry
from app import db

class AccountingService:
    @staticmethod
    def create_invoice(data):
        """Create invoice with automatic journal entries"""
        invoice = Invoice(**data)
        db.session.add(invoice)
        
        # Double-entry journal
        sales_entry = JournalEntry(
            debit_account="Accounts Receivable",
            credit_account="Sales Revenue",
            amount=invoice.total,
            reference_type="invoice",
            reference_id=invoice.id
        )
        tax_entry = JournalEntry(
            debit_account="Accounts Receivable",
            credit_account="Tax Payable",
            amount=invoice.tax,
            reference_type="invoice",
            reference_id=invoice.id
        )
        
        db.session.add_all([sales_entry, tax_entry])
        db.session.commit()
        return invoice

    @staticmethod
    def generate_trial_balance():
        """Dynamic trial balance calculation"""
        return db.session.query(
            JournalEntry.debit_account,
            db.func.sum(JournalEntry.amount).label('debit_total')
        ).group_by(JournalEntry.debit_account).all()