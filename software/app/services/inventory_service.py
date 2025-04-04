from app.models.accounting import Invoice, Voucher, InventoryItem, db
from datetime import datetime

def update_inventory_from_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return False
    
    for item in invoice.inventory_items:
        inventory_item = item.inventory_item
        if invoice.type == 'Purchase':
            inventory_item.quantity += item.quantity
        elif invoice.type == 'Sale':
            inventory_item.quantity -= item.quantity
        
        inventory_item.unit_price = item.unit_price
        inventory_item.last_updated = datetime.utcnow()
    
    db.session.commit()
    return True

def update_inventory_from_voucher(voucher_id):
    voucher = Voucher.query.get(voucher_id)
    if not voucher or voucher.voucher_type not in ['Payment', 'Receipt']:
        return False
    
    for item in voucher.inventory_items:
        inventory_item = item.inventory_item
        if voucher.voucher_type == 'Payment':  # Purchase payment
            inventory_item.quantity += item.quantity
        elif voucher.voucher_type == 'Receipt':  # Sale receipt
            inventory_item.quantity -= item.quantity
        
        inventory_item.last_updated = datetime.utcnow()
    
    db.session.commit()
    return True                 