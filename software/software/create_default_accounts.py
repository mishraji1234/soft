from app import create_app, db
from app.models.accounting import Account

app = create_app()

with app.app_context():
    # Create essential accounts if they don't exist
    accounts = [
        {'name': 'Accounts Receivable', 'account_type': 'Asset'},
        {'name': 'Accounts Payable', 'account_type': 'Liability'},
        {'name': 'Sales Revenue', 'account_type': 'Revenue'},
        {'name': 'Service Revenue', 'account_type': 'Revenue'},
        {'name': 'Cost of Goods Sold', 'account_type': 'Expense'}
    ]
    
    for acc_data in accounts:
        if not Account.query.filter_by(name=acc_data['name']).first():
            db.session.add(Account(**acc_data))
    
    db.session.commit()
    print("Default accounts created successfully")