from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Product, Order, OrderItem, ResaleListing
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ORDER_STATUSES = ['Placed', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
CATEGORIES = ['sofas', 'beds', 'tables', 'chairs', 'wardrobes', 'storage', 'lighting', 'decor']
STYLES = ['Modern', 'Minimalist', 'Traditional', 'Contemporary']


@admin_bp.route('/')
@admin_required
def dashboard():
    """Main administrative command center with real database counts."""
    total_users = User.query.filter_by(role='customer').count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_resale = ResaleListing.query.filter_by(status='Pending').count()

    completed_orders = Order.query.filter(Order.status != 'Cancelled').all()
    total_revenue = sum(o.total_amount for o in completed_orders)

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_resale = ResaleListing.query.order_by(ResaleListing.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        active_products=active_products,
        total_products=total_products,
        total_orders=total_orders,
        pending_resale=pending_resale,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        recent_resale=recent_resale
    )


# --- PRODUCT MANAGEMENT ---

@admin_bp.route('/products')
@admin_required
def products():
    """List of all products with status, stock, and management controls."""
    category_filter = request.args.get('category', 'all')
    query = Product.query

    if category_filter and category_filter != 'all':
        query = query.filter_by(category=category_filter)

    product_list = query.order_by(Product.id.desc()).all()
    return render_template(
        'admin/products.html',
        products=product_list,
        categories=CATEGORIES,
        current_category=category_filter
    )


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def product_new():
    """Adds a new furniture product into the catalog."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip().lower()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=int)
        material = request.form.get('material', '').strip()
        colour = request.form.get('colour', '').strip()
        dimensions = request.form.get('dimensions', '').strip()
        stock = request.form.get('stock', type=int)
        image_url = request.form.get('image_url', '').strip()
        room_types = request.form.get('room_types', 'Living Room').strip()
        style = request.form.get('style', 'Modern').strip()
        is_active = bool(request.form.get('is_active'))

        if not name or not category or not description or price is None or stock is None or not image_url:
            flash("Please fill in all mandatory product fields.", "danger")
            return render_template('admin/product_form.html', categories=CATEGORIES, styles=STYLES, product=None)

        new_prod = Product(
            name=name,
            category=category,
            description=description,
            price=price,
            material=material or 'Solid Wood',
            colour=colour or 'Natural',
            dimensions=dimensions or 'Standard',
            stock=stock,
            image_url=image_url,
            room_types=room_types,
            style=style,
            is_active=is_active
        )
        db.session.add(new_prod)
        db.session.commit()
        flash(f"Product '{new_prod.name}' created successfully.", "success")
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=CATEGORIES, styles=STYLES, product=None)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    """Edits an existing catalog product."""
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.category = request.form.get('category', '').strip().lower()
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', type=int)
        product.material = request.form.get('material', '').strip()
        product.colour = request.form.get('colour', '').strip()
        product.dimensions = request.form.get('dimensions', '').strip()
        product.stock = request.form.get('stock', type=int)
        product.image_url = request.form.get('image_url', '').strip()
        product.room_types = request.form.get('room_types', 'Living Room').strip()
        product.style = request.form.get('style', 'Modern').strip()
        product.is_active = bool(request.form.get('is_active'))

        db.session.commit()
        flash(f"Updated '{product.name}' successfully.", "success")
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=CATEGORIES, styles=STYLES, product=product)


@admin_bp.route('/products/toggle/<int:product_id>', methods=['POST'])
@admin_required
def product_toggle(product_id):
    """Toggles active/inactive visibility status of a product."""
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    status_str = "activated" if product.is_active else "deactivated"
    flash(f"Product '{product.name}' {status_str}.", "info")
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/stock/<int:product_id>', methods=['POST'])
@admin_required
def product_stock_update(product_id):
    """Quick update for inventory stock quantity."""
    product = Product.query.get_or_404(product_id)
    new_stock = request.form.get('stock', type=int)
    if new_stock is not None and new_stock >= 0:
        product.stock = new_stock
        db.session.commit()
        flash(f"Stock for '{product.name}' set to {new_stock}.", "success")
    return redirect(url_for('admin.products'))


# --- ORDERS MANAGEMENT ---

@admin_bp.route('/orders')
@admin_required
def orders():
    """All customer orders with status filter and update modal."""
    status_filter = request.args.get('status', 'all')
    query = Order.query

    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)

    order_list = query.order_by(Order.created_at.desc()).all()
    return render_template(
        'admin/orders.html',
        orders=order_list,
        order_statuses=ORDER_STATUSES,
        current_status=status_filter
    )


@admin_bp.route('/orders/status/<int:order_id>', methods=['POST'])
@admin_required
def order_status_update(order_id):
    """Updates order fulfillment status, handling stock restoration upon cancellation."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    if new_status in ORDER_STATUSES and new_status != order.status:
        old_status = order.status
        order.status = new_status

        # If order was cancelled, restore stock
        if new_status == 'Cancelled' and old_status != 'Cancelled':
            for item in order.items:
                if item.product:
                    item.product.stock += item.quantity
            flash(f"Order #{order.order_number} cancelled and product stocks restored.", "info")
        # If un-cancelled, deduct stock back
        elif old_status == 'Cancelled' and new_status != 'Cancelled':
            for item in order.items:
                if item.product:
                    item.product.stock = max(0, item.product.stock - item.quantity)
            flash(f"Order #{order.order_number} re-opened to '{new_status}'.", "info")
        else:
            flash(f"Order #{order.order_number} status updated to '{new_status}'.", "success")

        db.session.commit()

    return redirect(url_for('admin.orders'))


# --- RESALE MODERATION ---

@admin_bp.route('/resale')
@admin_required
def resale():
    """Moderation queue for user resale listings."""
    status_filter = request.args.get('status', 'Pending')
    query = ResaleListing.query

    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)

    listings = query.order_by(ResaleListing.created_at.desc()).all()
    pending_count = ResaleListing.query.filter_by(status='Pending').count()

    return render_template(
        'admin/resale.html',
        listings=listings,
        current_status=status_filter,
        pending_count=pending_count
    )


@admin_bp.route('/resale/moderate/<int:listing_id>', methods=['POST'])
@admin_required
def resale_moderate(listing_id):
    """Approves or rejects a resale listing with optional admin notes."""
    listing = ResaleListing.query.get_or_404(listing_id)
    action = request.form.get('action')  # 'approve' or 'reject'
    admin_notes = request.form.get('admin_notes', '').strip()

    if action == 'approve':
        listing.status = 'Approved'
        listing.admin_notes = admin_notes or "Approved for marketplace listing."
        flash(f"Listing '{listing.title}' approved and published to public marketplace.", "success")
    elif action == 'reject':
        listing.status = 'Rejected'
        listing.admin_notes = admin_notes or "Listing does not comply with FurniSpace standards."
        flash(f"Listing '{listing.title}' rejected.", "warning")

    db.session.commit()
    return redirect(url_for('admin.resale'))
