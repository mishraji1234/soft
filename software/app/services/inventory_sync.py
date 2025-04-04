from flask_socketio import SocketIO, emit
from app import socketio

def sync_inventory_update(item_id):
    """Push real-time updates to all clients"""
    item = InventoryItem.query.get(item_id)
    socketio.emit('inventory_update', {
        'id': item.id,
        'item_name': item.item_name,
        'quantity': item.quantity,
        'unit_price': item.unit_price,
        'last_updated': item.last_updated.isoformat()
    }, namespace='/inventory')