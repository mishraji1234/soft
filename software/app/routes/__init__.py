from flask import Blueprint

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')
vouchers_bp = Blueprint('vouchers', __name__, url_prefix='/vouchers')
auth_bp = Blueprint('login', __name__, url_prefix='/login')
journals_bp = Blueprint('journals', __name__, url_prefix='/journals')
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')
