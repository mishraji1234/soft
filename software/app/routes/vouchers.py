from app.routes import vouchers_bp

@vouchers_bp.route('/')
def list_vouchers():
    return "VOUCHERS ARE WORKING!"