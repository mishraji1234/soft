from flask import render_template, jsonify
from app.models.accounting import InventoryItem
from app.extensions import db
from app.routes import inventory_bp
from datetime import datetime, timedelta

@inventory_bp.route('/')
def list_inventory():
    items = InventoryItem.query.order_by(InventoryItem.item_name).all()
    return render_template('inventory.html', items=items)

@inventory_bp.route('/data')
def inventory_data():
    items = InventoryItem.query.options(
        db.joinedload(InventoryItem.invoice_items),
        db.joinedload(InventoryItem.voucher_items)
    ).order_by(InventoryItem.item_name).all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'item_name': item.item_name,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'last_updated': item.last_updated.strftime('%Y-%m-%d %H:%M'),
            'total_value': float(item.quantity * item.unit_price)
        } for item in items]
    })