from flask import render_template, jsonify, request
from app.models.accounting import JournalEntry, Account
from app.extensions import db
from app.routes import journals_bp
from datetime import datetime

@journals_bp.route('/')
def list_journals():
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    account_id = request.args.get('account_id')
    
    # Base query
    query = JournalEntry.query.options(
        db.joinedload(JournalEntry.lines),
        db.joinedload(JournalEntry.debit_account),
        db.joinedload(JournalEntry.credit_account)
    )
    
    # Apply filters
    if date_from:
        query = query.filter(JournalEntry.entry_date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(JournalEntry.entry_date <= datetime.strptime(date_to, '%Y-%m-%d'))
    if account_id:
        query = query.filter(
            (JournalEntry.debit_account_id == account_id) | 
            (JournalEntry.credit_account_id == account_id)
        )
    
    entries = query.order_by(JournalEntry.entry_date.desc()).all()
    
    # Calculate totals
    total_debits = db.session.query(
        db.func.sum(JournalEntry.amount)
    ).filter(JournalEntry.debit_account_id.isnot(None)).scalar() or 0.00
    
    total_credits = db.session.query(
        db.func.sum(JournalEntry.amount)
    ).filter(JournalEntry.credit_account_id.isnot(None)).scalar() or 0.00
    
    ledger_accounts = Account.query.order_by(Account.account_name).all()
    
    return render_template('journals.html',
                         entries=entries,
                         total_debits=total_debits,
                         total_credits=total_credits,
                         ledger_accounts=ledger_accounts)

@journals_bp.route('/data')
def journals_data():
    entries = JournalEntry.query.options(
        db.joinedload(JournalEntry.lines),
        db.joinedload(JournalEntry.debit_account),
        db.joinedload(JournalEntry.credit_account)
    ).order_by(JournalEntry.entry_date.desc()).limit(50).all()
    
    total_debits = db.session.query(
        db.func.sum(JournalEntry.amount)
    ).filter(JournalEntry.debit_account_id.isnot(None)).scalar() or 0.00
    
    total_credits = db.session.query(
        db.func.sum(JournalEntry.amount)
    ).filter(JournalEntry.credit_account_id.isnot(None)).scalar() or 0.00
    
    return jsonify({
        'journals': [{
            'id': e.id,
            'entry_date': e.entry_date.strftime('%Y-%m-%d %H:%M'),
            'description': e.description,
            'amount': float(e.amount),
            'is_posted': e.is_posted,
            'debit_account': e.debit_account.account_name if e.debit_account else '',
            'debit_account_no': e.debit_account.account_no if e.debit_account else '',
            'credit_account': e.credit_account.account_name if e.credit_account else '',
            'credit_account_no': e.credit_account.account_no if e.credit_account else '',
            'transaction_type': e.transaction_type,
            'transaction_id': e.transaction_id
        } for e in entries],
        'total_debits': float(total_debits),
        'total_credits': float(total_credits)
    })