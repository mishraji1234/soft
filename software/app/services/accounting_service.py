from app.models.accounting import Account, JournalEntry, JournalEntryLine, Invoice, Voucher
from app import db

def get_account(account_name):
    """Safe account retrieval with error handling"""
    account = Account.query.filter_by(name=account_name).first()
    if not account:
        raise ValueError(f"Account '{account_name}' not found in database")
    return account

def get_account_by_name(name):
    account = Account.query.filter_by(name=name).first()
    if not account:
        raise ValueError(f"Account '{name}' not found in database")
    return account

def create_invoice_journal(invoice):
    """Create journal entry for new invoices"""
    try:
        if invoice.type == 'Sale':
            debit_account = Account.query.filter_by(name='Accounts Receivable').first()
            credit_account = Account.query.filter_by(name=invoice.sub_account).first()
        else:  # Purchase
            debit_account = Account.query.filter_by(name=invoice.sub_account).first()
            credit_account = Account.query.filter_by(name='Accounts Payable').first()

        journal = JournalEntry(
            date=invoice.date,
            reference=f"INV-{invoice.id}",
            description=f"Invoice {invoice.customer_name}",
            source_type='invoice',
            source_id=invoice.id
        )
        
        journal.lines.append(JournalEntryLine(
            debit_account_id=debit_account.id,
            credit_account_id=credit_account.id,
            amount=invoice.base_amount,
            vat_amount=invoice.vat,
            withholding_tax_amount=invoice.withholding_tax
        ))
        
        return journal
    except Exception as e:
        raise ValueError(f"Journal creation failed: {str(e)}")
        

def create_voucher_journal(voucher):
    """Creates journal entries when vouchers are saved"""
    if voucher.voucher_type == 'Payment':
        debit_account = get_account_by_name(voucher.account_type)
        credit_account = get_account_by_name('Cash')
    elif voucher.voucher_type == 'Receipt':
        debit_account = get_account_by_name('Cash')
        credit_account = get_account_by_name(voucher.account_type)
    else:  # Purchase
        debit_account = get_account_by_name(voucher.account_type)
        credit_account = get_account_by_name('Accounts Payable')
    
    journal = JournalEntry(
        date=voucher.date,
        reference=voucher.voucher_number,
        description=f"{voucher.voucher_type} Voucher",
        source_type='voucher',
        source_id=voucher.id,
        is_posted=True
    )
    
    journal.lines.append(JournalEntryLine(
        debit_account_id=debit_account.id,
        credit_account_id=credit_account.id,
        amount=voucher.total_amount,
        vat_amount=voucher.vat,
        withholding_tax_amount=voucher.withhold_tax
    ))
    
    db.session.add(journal)
    voucher.journal_entry = journal
    return journal

def update_ledger_balances(journal_entry):
    """Updates ledger balances when journal entries are posted"""
    for line in journal_entry.lines:
        if line.debit_account:
            line.debit_account.balance += line.amount
        if line.credit_account:
            line.credit_account.balance -= line.amount
    db.session.comm
    
    
    
#@accounting_bp.route('/dashboard')
def dashboard():
    # Only query data that exists in your database
    return render_template('dashboard.html')
    


def update_invoice_journal(invoice):
    """Update journal entry when invoice is modified"""
    try:
        if not invoice.journal_entry:
            raise ValueError("No journal entry exists for this invoice")

        journal = invoice.journal_entry
        journal.date = invoice.date
        journal.description = f"Invoice {invoice.customer_name}"

        # Get accounts based on invoice type
        if invoice.type == 'Sale':
            debit_account = get_account_by_name('Accounts Receivable')
            credit_account = get_account_by_name(invoice.sub_account)
        else:  # Purchase
            debit_account = get_account_by_name(invoice.sub_account)
            credit_account = get_account_by_name('Accounts Payable')

        # Update the journal line (assuming one line per invoice)
        if journal.lines:
            line = journal.lines[0]
            line.debit_account_id = debit_account.id
            line.credit_account_id = credit_account.id
            line.amount = invoice.base_amount
            line.vat_amount = invoice.vat
            line.withholding_tax_amount = invoice.withholding_tax
        else:
            # Create new line if none exists (shouldn't happen)
            journal.lines.append(JournalEntryLine(
                debit_account_id=debit_account.id,
                credit_account_id=credit_account.id,
                amount=invoice.base_amount,
                vat_amount=invoice.vat,
                withholding_tax_amount=invoice.withholding_tax
            ))

        return journal

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Failed to update invoice journal: {str(e)}")