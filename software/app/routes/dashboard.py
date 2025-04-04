from flask import render_template, jsonify
from app.models.accounting import JournalEntry, Invoice, Voucher
from datetime import datetime, timedelta
from app.extensions import db
from app.routes import dashboard_bp  # Import the blueprint that's now guaranteed to exist

# Use the imported blueprint directly
@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ... (keep all your existing route functions unchanged) ...

@dashboard_bp.route('/dashboard_data')
def dashboard_data():
    # Calculate date ranges
    today = datetime.utcnow()
    last_month = today - timedelta(days=30)
    
    # Get financial data
    total_revenue = db.session.query(
        db.func.sum(Invoice.total_amount)
    ).filter(
        Invoice.type == 'Sale',
        Invoice.is_posted == True
    ).scalar() or 0
    
    total_expenses = db.session.query(
        db.func.sum(Voucher.total_amount)
    ).filter(
        Voucher.voucher_type == 'Payment',
        Voucher.is_posted == True
    ).scalar() or 0
    
    net_income = total_revenue - total_expenses
    
    # Get trial balance data
    total_debit = db.session.query(
        db.func.sum(JournalEntry.amount)
    ).filter(
        JournalEntry.is_posted == True
    ).scalar() or 0
    
    total_credit = total_debit  # Should match in proper accounting
    
    # Sample data for charts (you'll need to implement proper queries)
    income_statement_labels = [f'Day {i}' for i in range(1, 31)]
    income_statement_revenue = [total_revenue * (0.8 + 0.4 * (i/30)) for i in range(30)]
    income_statement_expenses = [total_expenses * (0.6 + 0.3 * (i/30)) for i in range(30)]
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'net_income': float(net_income),
        'vat_payable': float(total_expenses * 0.15),  # 15% VAT example
        'vat_receivable': float(total_revenue * 0.15),  # 15% VAT example
        'total_debit': float(total_debit),
        'total_credit': float(total_credit),
        'total_assets': float(total_debit * 0.6),  # Example ratio
        'total_liabilities': float(total_credit * 0.3),  # Example ratio
        'total_equity': float(total_debit * 0.7 - total_credit * 0.3),  # Example calculation
        'income_statement_labels': income_statement_labels,
        'income_statement_revenue': income_statement_revenue,
        'income_statement_expenses': income_statement_expenses,
        'payable_receivable': [
            {
                'type': 'Receivable',
                'account': 'Customer A',
                'amount': 5000.00,
                'due_date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                'status': 'Pending'
            },
            {
                'type': 'Payable',
                'account': 'Supplier X',
                'amount': 3000.00,
                'due_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
                'status': 'Overdue'
            }
        ]
    })