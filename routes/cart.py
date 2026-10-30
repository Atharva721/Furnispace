import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, Product, CartItem, Order, OrderItem
from routes.auth import get_current_user, login_required

cart_bp = Blueprint('cart', __name__)


def _get_cart_items():
    """Returns a list of dicts with item, product, quantity, subtotal."""
    user = get_current_user()
    items = []
    if user:
        # Load from database
        db_items = CartItem.query.filter_by(user_id=user.id).all()
        for ci in db_items:
            if ci.product and ci.product.is_active:
                items.append({
                    'id': ci.id,
                    'product': ci.product,
                    'quantity': ci.quantity,
                    'subtotal': ci.subtotal
                })
    else:
        # Load from session guest cart
        guest_cart = session.get('guest_cart', {})
        for pid_str, qty in guest_cart.items():
            product = Product.query.get(int(pid_str))
            if product and product.is_active:
                items.append({
                    'id': f"guest_{product.id}",
                    'product': product,
                    'quantity': qty,
                    'subtotal': product.price * qty
                })
    return items


@cart_bp.route('/cart')
def index():
    """Displays the current shopping cart with totals and quantity modifiers."""
    cart_items = _get_cart_items()
    total = sum(item['subtotal'] for item in cart_items)
    return render_template('cart/index.html', cart_items=cart_items, total=total)


@cart_bp.route('/cart/add/<int:product_id>', methods=['POST', 'GET'])
def add(product_id):
    """Adds a product to the cart with server-side stock validation."""
    product = Product.query.get_or_404(product_id)
    if not product.is_active:
        flash("Sorry, this product is no longer active.", "danger")
        return redirect(url_for('shop.index'))

    if product.stock <= 0:
        flash(f"'{product.name}' is currently out of stock.", "warning")
        return redirect(request.referrer or url_for('shop.product_detail', product_id=product_id))

    try:
        qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        qty = 1

    if qty <= 0:
        qty = 1

    user = get_current_user()
    if user:
        # DB Cart
        cart_entry = CartItem.query.filter_by(user_id=user.id, product_id=product.id).first()
        current_qty = cart_entry.quantity if cart_entry else 0
        new_qty = current_qty + qty

        if new_qty > product.stock:
            available = product.stock - current_qty
            if available > 0:
                new_qty = product.stock
                flash(f"Only {available} more units available in stock. Added maximum available.", "warning")
            else:
                flash(f"You already have the maximum available stock ({product.stock}) in your cart.", "warning")
                return redirect(url_for('cart.index'))

        if cart_entry:
            cart_entry.quantity = new_qty
        else:
            cart_entry = CartItem(user_id=user.id, product_id=product.id, quantity=new_qty)
            db.session.add(cart_entry)
        db.session.commit()
    else:
        # Session Guest Cart
        guest_cart = session.get('guest_cart', {})
        pid_str = str(product.id)
        current_qty = guest_cart.get(pid_str, 0)
        new_qty = current_qty + qty

        if new_qty > product.stock:
            new_qty = product.stock
            flash(f"Added maximum available quantity ({product.stock}) to cart.", "warning")

        guest_cart[pid_str] = new_qty
        session['guest_cart'] = guest_cart

    flash(f"Added {product.name} to your cart.", "success")
    return redirect(request.referrer or url_for('cart.index'))


@cart_bp.route('/cart/update/<path:item_id>', methods=['POST'])
def update(item_id):
    """Updates the quantity of a specific cart item."""
    try:
        new_qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        new_qty = 1

    user = get_current_user()
    if user and not item_id.startswith('guest_'):
        cart_entry = CartItem.query.filter_by(id=int(item_id), user_id=user.id).first()
        if cart_entry:
            if new_qty <= 0:
                db.session.delete(cart_entry)
                flash(f"Removed '{cart_entry.product.name}' from your cart.", "info")
            elif new_qty > cart_entry.product.stock:
                cart_entry.quantity = cart_entry.product.stock
                flash(f"Quantity capped to maximum available stock ({cart_entry.product.stock}).", "warning")
            else:
                cart_entry.quantity = new_qty
                flash("Cart updated successfully.", "success")
            db.session.commit()
    else:
        # Guest cart
        pid_str = item_id.replace('guest_', '')
        guest_cart = session.get('guest_cart', {})
        if pid_str in guest_cart:
            product = Product.query.get(int(pid_str))
            if new_qty <= 0:
                del guest_cart[pid_str]
                flash("Item removed from cart.", "info")
            elif product and new_qty > product.stock:
                guest_cart[pid_str] = product.stock
                flash(f"Quantity capped to maximum available stock ({product.stock}).", "warning")
            else:
                guest_cart[pid_str] = new_qty
                flash("Cart updated.", "success")
            session['guest_cart'] = guest_cart

    return redirect(url_for('cart.index'))


@cart_bp.route('/cart/remove/<path:item_id>', methods=['POST', 'GET'])
def remove(item_id):
    """Removes an item completely from cart."""
    user = get_current_user()
    if user and not item_id.startswith('guest_'):
        cart_entry = CartItem.query.filter_by(id=int(item_id), user_id=user.id).first()
        if cart_entry:
            name = cart_entry.product.name if cart_entry.product else "Item"
            db.session.delete(cart_entry)
            db.session.commit()
            flash(f"Removed '{name}' from your cart.", "info")
    else:
        pid_str = item_id.replace('guest_', '')
        guest_cart = session.get('guest_cart', {})
        if pid_str in guest_cart:
            del guest_cart[pid_str]
            session['guest_cart'] = guest_cart
            flash("Item removed from cart.", "info")

    return redirect(url_for('cart.index'))


@cart_bp.route('/cart/clear', methods=['POST', 'GET'])
def clear():
    """Clears all items from the cart."""
    user = get_current_user()
    if user:
        CartItem.query.filter_by(user_id=user.id).delete()
        db.session.commit()
    session['guest_cart'] = {}
    flash("Your shopping cart has been cleared.", "info")
    return redirect(url_for('cart.index'))


# --- DEMO CHECKOUT & ORDERS ---

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Demo checkout page. Requires user login and validates atomic stock updates."""
    user = get_current_user()
    if not user:
        flash("Please log in or register to complete your order.", "warning")
        return redirect(url_for('auth.login', next=url_for('cart.checkout')))

    # Ensure guest cart items are merged if any
    guest_cart = session.get('guest_cart', {})
    if guest_cart:
        for pid_str, qty in guest_cart.items():
            product = Product.query.get(int(pid_str))
            if product and product.is_active and product.stock > 0:
                existing = CartItem.query.filter_by(user_id=user.id, product_id=product.id).first()
                if existing:
                    existing.quantity = min(existing.quantity + qty, product.stock)
                else:
                    db.session.add(CartItem(user_id=user.id, product_id=product.id, quantity=min(qty, product.stock)))
        db.session.commit()
        session['guest_cart'] = {}

    cart_entries = CartItem.query.filter_by(user_id=user.id).all()
    if not cart_entries:
        flash("Your cart is empty. Add items before checking out.", "warning")
        return redirect(url_for('shop.index'))

    # Calculate total and verify stock
    total_amount = 0
    stock_issues = []
    for entry in cart_entries:
        if not entry.product or not entry.product.is_active:
            stock_issues.append("An item in your cart is no longer active.")
        elif entry.quantity > entry.product.stock:
            stock_issues.append(f"'{entry.product.name}' only has {entry.product.stock} items remaining.")
        else:
            total_amount += entry.product.price * entry.quantity

    if stock_issues:
        for issue in stock_issues:
            flash(issue, "danger")
        return redirect(url_for('cart.index'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        delivery_address = request.form.get('delivery_address', '').strip()

        if not customer_name or not customer_phone or not delivery_address:
            flash("Please fill in all shipping details.", "danger")
            return render_template(
                'cart/checkout.html',
                cart_entries=cart_entries,
                total=total_amount,
                user=user
            )

        # Atomic transaction: Create order, create items, decrement stock, clear cart
        try:
            # Re-lock / re-verify stock inside transaction
            for entry in cart_entries:
                if entry.quantity > entry.product.stock:
                    raise ValueError(f"Insufficient stock for {entry.product.name}")

            order_number = f"FS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            new_order = Order(
                order_number=order_number,
                user_id=user.id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                delivery_address=delivery_address,
                total_amount=total_amount,
                status='Placed'
            )
            db.session.add(new_order)
            db.session.flush()  # populate order.id

            for entry in cart_entries:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=entry.product_id,
                    product_name=entry.product.name,
                    unit_price=entry.product.price,
                    quantity=entry.quantity
                )
                db.session.add(order_item)
                # Safely reduce stock
                entry.product.stock = max(0, entry.product.stock - entry.quantity)

            # Clear cart only after successful order creation
            CartItem.query.filter_by(user_id=user.id).delete()

            db.session.commit()
            flash("Order placed successfully! Thank you for choosing FurniSpace.", "success")
            return redirect(url_for('cart.confirmation', order_number=order_number))

        except Exception as e:
            db.session.rollback()
            flash(f"Order placement failed: {str(e)}", "danger")
            return redirect(url_for('cart.index'))

    return render_template(
        'cart/checkout.html',
        cart_entries=cart_entries,
        total=total_amount,
        user=user
    )


@cart_bp.route('/order/confirmation/<string:order_number>')
@login_required
def confirmation(order_number):
    """Order confirmation receipt with order summary."""
    user = get_current_user()
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != user.id and not user.is_admin():
        flash("You are not authorized to view this order.", "danger")
        return redirect(url_for('shop.index')), 403

    return render_template('cart/confirmation.html', order=order)


@cart_bp.route('/orders')
@login_required
def orders():
    """List of orders placed by the currently logged-in customer."""
    user = get_current_user()
    user_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('cart/orders.html', orders=user_orders)


@cart_bp.route('/order/<string:order_number>')
@login_required
def order_detail(order_number):
    """Detailed view for a specific order."""
    user = get_current_user()
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != user.id and not user.is_admin():
        flash("Access denied.", "danger")
        return redirect(url_for('cart.orders')), 403

    return render_template('cart/order_detail.html', order=order)
