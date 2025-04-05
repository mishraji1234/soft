from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.routes import (
        invoices_bp, vouchers_bp, journals_bp,
        inventory_bp, reports_bp, auth_bp
    )
    
    app.register_blueprint(invoices_bp)
    app.register_blueprint(vouchers_bp)
    app.register_blueprint(journals_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(auth_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        create_default_accounts()
    
    return app

def create_default_accounts():
    from app.models.accounting import Account
    default_accounts = [
        # Assets
        {'code': '1000', 'name': 'Cash', 'account_type': 'asset'},
        {'code': '1010', 'name': 'Petty Cash', 'account_type': 'asset'},
        {'code': '1020', 'name': 'Bank Account', 'account_type': 'asset'},
        {'code': '1100', 'name': 'Accounts Receivable', 'account_type': 'asset'},
        {'code': '1200', 'name': 'Inventory', 'account_type': 'asset'},
        {'code': '1300', 'name': 'Prepaid Expenses', 'account_type': 'asset'},
        {'code': '1400', 'name': 'Fixed Assets', 'account_type': 'asset'},
        {'code': '1410', 'name': 'Accumulated Depreciation', 'account_type': 'asset'},

        # Liabilities
        {'code': '2000', 'name': 'Accounts Payable', 'account_type': 'liability'},
        {'code': '2100', 'name': 'Accrued Expenses', 'account_type': 'liability'},
        {'code': '2200', 'name': 'VAT Payable', 'account_type': 'liability'},
        {'code': '2300', 'name': 'Withholding Tax Payable', 'account_type': 'liability'},
        {'code': '2400', 'name': 'Loan Payable', 'account_type': 'liability'},

        # Equity
        {'code': '3000', 'name': 'Owner’s Capital', 'account_type': 'equity'},
        {'code': '3100', 'name': 'Retained Earnings', 'account_type': 'equity'},
        {'code': '3200', 'name': 'Owner’s Drawings', 'account_type': 'equity'},

        # Income / Revenue
        {'code': '4000', 'name': 'Sales Revenue', 'account_type': 'income'},
        {'code': '4100', 'name': 'Service Revenue', 'account_type': 'income'},
        {'code': '4200', 'name': 'Other Income', 'account_type': 'income'},
        {'code': '4300', 'name': 'VAT Collected', 'account_type': 'income'},

        # Expenses
        {'code': '5000', 'name': 'Cost of Goods Sold', 'account_type': 'expense'},
        {'code': '5100', 'name': 'Salaries and Wages', 'account_type': 'expense'},
        {'code': '5200', 'name': 'Rent Expense', 'account_type': 'expense'},
        {'code': '5300', 'name': 'Utilities Expense', 'account_type': 'expense'},
        {'code': '5400', 'name': 'Office Supplies', 'account_type': 'expense'},
        {'code': '5500', 'name': 'Depreciation Expense', 'account_type': 'expense'},
        {'code': '5600', 'name': 'Advertising Expense', 'account_type': 'expense'},
        {'code': '5700', 'name': 'Transportation Expense', 'account_type': 'expense'},
        {'code': '5800', 'name': 'Withholding Tax Paid', 'account_type': 'expense'},
        {'code': '5900', 'name': 'Bank Charges', 'account_type': 'expense'},
    ]
    
    for acc in default_accounts:
        if not Account.query.filter_by(code=acc['code']).first():
            db.session.add(Account(**acc))
    db.session.commit()

    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)