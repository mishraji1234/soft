from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import func, case
from app.models.accounting import (
    db, Account, JournalEntry, Inventory, 
    Invoice, Voucher, InvoiceItem
)

accounting_bp = Blueprint('accounting', __name__)

@accounting_bp.route('/journals')
@login_required
def journals():
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    account_id = request.args.get('account_id')
    
    # Build query
    query = db.session.query(
        JournalEntry,
        Account.account_name.label('debit_account'),
        Account.account_name.label('credit_account')
    ).join(
        Account, JournalEntry.debit_account_id == Account.id
    ).join(
        Account, JournalEntry.credit_account_id == Account.id
    ).order_by(JournalEntry.date.desc())
    
    # Apply filters
    if date_from:
        query = query.filter(JournalEntry.date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(JournalEntry.date <= datetime.strptime(date_to, '%Y-%m-%d'))
    if account_id:
        query = query.filter(
            (JournalEntry.debit_account_id == account_id) | 
            (JournalEntry.credit_account_id == account_id)
        )
    
    entries = query.all()
    
    # Calculate totals
    totals = db.session.query(
        func.sum(JournalEntry.amount).label('total_debits')
    ).filter(
        JournalEntry.id.in_([e.JournalEntry.id for e in entries])
    ).first()
    
    return render_template('journals.html', 
                         entries=entries,
                         total_debits=totals.total_debits or 0,
                         total_credits=totals.total_debits or 0)  # Debits = Credits in double-entry

@accounting_bp.route('/journals/data')
@login_required
def journals_data():
    # API endpoint for DataTables
    entries = JournalEntry.query.order_by(JournalEntry.date.desc()).limit(100).all()
    return jsonify({
        'data': [{
            'id': e.id,
            'date': e.date.strftime('%Y-%m-%d'),
            'description': e.description,
            'debit_account': e.debit_account.account_name,
            'credit_account': e.credit_account.account_name,
            'amount': float(e.amount),
            'reference_type': e.reference_type,
            'reference_id': e.reference_id,
            'is_posted': e.is_posted
        } for e in entries]
    })

@accounting_bp.route('/inventory')
@login_required
def inventory():
    items = Inventory.query.order_by(Inventory.name).all()
    return render_template('inventory.html', items=items)

@accounting_bp.route('/inventory/data')
@login_required
def inventory_data():
    items = Inventory.query.all()
    return jsonify({
        'data': [{
            'id': item.id,
            'name': item.name,
            'quantity': item.quantity,
            'unit_cost': float(item.unit_cost),
            'total_value': float(item.quantity * item.unit_cost),
            'last_updated': item.last_updated.strftime('%Y-%m-%d %H:%M')
        } for item in items]
    })

@accounting_bp.route('/ledger')
@login_required
def ledger():
    # Group journal entries by account
    ledger_data = db.session.query(
        Account,
        func.sum(case(
            [(JournalEntry.debit_account_id == Account.id, JournalEntry.amount)],
            else_=0
        )).label('total_debits'),
        func.sum(case(
            [(JournalEntry.credit_account_id == Account.id, JournalEntry.amount)],
            else_=0
        )).label('total_credits')
    ).join(
        JournalEntry,
        (Account.id == JournalEntry.debit_account_id) | (Account.id == JournalEntry.credit_account_id)
    ).group_by(
        Account.id
    ).all()
    
    # Calculate balances
    ledger = []
    for account, debits, credits in ledger_data:
        if account.normal_balance == 'DR':
            balance = debits - credits
        else:
            balance = credits - debits
        ledger.append({
            'account': account,
            'debits': debits or 0,
            'credits': credits or 0,
            'balance': balance
        })
    
    return render_template('ledger.html', ledger=ledger)

@accounting_bp.route('/reports/trial_balance')
@login_required
def trial_balance():
    # Get balances for all accounts
    trial_balance = db.session.query(
        Account.account_type,
        Account.account_name,
        func.sum(case(
            [(JournalEntry.debit_account_id == Account.id, JournalEntry.amount)],
            else_=0
        )).label('debits'),
        func.sum(case(
            [(JournalEntry.credit_account_id == Account.id, JournalEntry.amount)],
            else_=0
        )).label('credits')
    ).join(
        JournalEntry,
        (Account.id == JournalEntry.debit_account_id) | (Account.id == JournalEntry.credit_account_id)
    ).group_by(
        Account.id
    ).order_by(
        Account.account_type,
        Account.account_name
    ).all()
    
    return render_template('trial_balance.html', trial_balance=trial_balance)

@accounting_bp.route('/reports/income_statement')
@login_required
def income_statement():
    # Get revenue and expenses for current period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    revenue = db.session.query(
        func.sum(JournalEntry.amount)
    ).join(
        Account,
        JournalEntry.credit_account_id == Account.id
    ).filter(
        Account.account_type == 'income',
        JournalEntry.date.between(start_date, end_date)
    ).scalar() or 0
    
    expenses = db.session.query(
        func.sum(JournalEntry.amount)
    ).join(
        Account,
        JournalEntry.debit_account_id == Account.id
    ).filter(
        Account.account_type == 'expense',
        JournalEntry.date.between(start_date, end_date)
    ).scalar() or 0
    
    net_income = revenue - expenses
    
    return render_template('income_statement.html',
                         revenue=revenue,
                         expenses=expenses,
                         net_income=net_income)

@accounting_bp.route('/reports/balance_sheet')
@login_required
def balance_sheet():
    # Get account balances by type
    balances = db.session.query(
        Account.account_type,
        func.sum(case(
            [
                (Account.account_type.in_(['asset', 'expense']), 
                 func.coalesce(JournalEntry.amount, 0)),
            ],
            else_=-func.coalesce(JournalEntry.amount, 0)
        )).label('balance')
    ).join(
        JournalEntry,
        (Account.id == JournalEntry.debit_account_id) | (Account.id == JournalEntry.credit_account_id)
    ).group_by(
        Account.account_type
    ).all()
    
    # Calculate totals
    assets = next((b.balance for b in balances if b.account_type == 'asset'), 0)
    liabilities = next((b.balance for b in balances if b.account_type == 'liability'), 0)
    equity = next((b.balance for b in balances if b.account_type == 'equity'), 0)
    
    return render_template('balance_sheet.html',
                         assets=assets,
                         liabilities=liabilities,
                         equity=equity)


def register_accounting_routes(bp):
    @bp.route('/journals')
    @login_required
    def journals():
        entries = JournalEntry.query.order_by(JournalEntry.date.desc()).all()
        return render_template('journals.html', entries=entries)
    
    @bp.route('/ledger')
    @login_required
    def ledger():
        accounts = Account.query.all()
        return render_template('ledger.html', accounts=accounts)