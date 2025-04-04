from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.routes import invoices_bp
from app.models.accounting import Invoice, JournalEntry
from app.forms import InvoiceForm

@invoices_bp.route('/')
@login_required
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('invoices/list.html', invoices=invoices)

@invoices_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_invoice():
    form = InvoiceForm()
    if form.validate_on_submit():
        try:
            invoice = Invoice(
                number=form.number.data,
                date=form.date.data,
                customer_name=form.customer_name.data,
                type=form.type.data,
                total_amount=form.total_amount.data,
                created_by=current_user.id
            )
            db.session.add(invoice)
            db.session.commit()
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('invoices.list_invoices'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating invoice: {str(e)}', 'danger')
    
    return render_template('invoices/add.html', form=form)

@invoices_bp.route('/<int:id>/post', methods=['POST'])
@login_required
def post_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'posted'
    db.session.commit()
    flash('Invoice posted with journal entries created!', 'success')
    return redirect(url_for('invoices.list_invoices'))

@invoices_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    try:
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting invoice: {str(e)}', 'danger')
    return redirect(url_for('invoices.list_invoices'))