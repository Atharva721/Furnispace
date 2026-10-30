from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Product, CartItem
from recommendation import recommend_room_bundle
from routes.auth import get_current_user

room_planner_bp = Blueprint('room_planner', __name__, url_prefix='/room-planner')

ROOM_TYPES = ['Living Room', 'Bedroom', 'Dining Room', 'Study Room']
STYLES = ['Any', 'Modern', 'Minimalist', 'Traditional', 'Contemporary']


@room_planner_bp.route('/', methods=['GET'])
def index():
    """Form to initiate Complete My Room budget planning."""
    return render_template('room_planner/index.html', room_types=ROOM_TYPES, styles=STYLES)


@room_planner_bp.route('/recommend', methods=['GET', 'POST'])
def recommend():
    """Calculates and displays the room bundle recommendation."""
    if request.method == 'POST':
        room_type = request.form.get('room_type', 'Living Room')
        budget = request.form.get('budget', type=int) or 50000
        style = request.form.get('style', 'Any')
        selected_ids_str = request.form.get('selected_ids', '')
    else:
        room_type = request.args.get('room_type', 'Living Room')
        budget = request.args.get('budget', type=int) or 50000
        style = request.args.get('style', 'Any')
        selected_ids_str = request.args.get('selected_ids', '')

    result = recommend_room_bundle(room_type=room_type, budget=budget, style=style)

    # If specific customized items were selected through replacement
    if selected_ids_str:
        try:
            custom_ids = [int(x.strip()) for x in selected_ids_str.split(',') if x.strip()]
            if custom_ids:
                custom_products = Product.query.filter(
                    Product.id.in_(custom_ids),
                    Product.is_active.is_(True),
                    Product.stock > 0
                ).all()
                custom_total = sum(p.price for p in custom_products)
                if custom_total <= budget:
                    result['items'] = custom_products
                    result['bundle_items'] = custom_products
                    result['total_price'] = custom_total
                    result['remaining_budget'] = budget - custom_total
                else:
                    flash(f"Custom selection exceeds budget by ₹{custom_total - budget:,}. Kept within recommended budget.", "warning")
        except Exception:
            pass

    return render_template(
        'room_planner/results.html',
        result=result,
        room_types=ROOM_TYPES,
        styles=STYLES,
        current_room=room_type,
        current_budget=budget,
        current_style=style
    )


@room_planner_bp.route('/add-bundle', methods=['POST'])
def add_bundle():
    """Adds all items from the recommended bundle directly into cart."""
    product_ids_raw = request.form.getlist('product_ids')
    if not product_ids_raw:
        # Fallback to comma-separated field
        selected_ids = request.form.get('selected_ids', '')
        product_ids_raw = [x.strip() for x in selected_ids.split(',') if x.strip()]

    if not product_ids_raw:
        flash("No products found in bundle to add.", "warning")
        return redirect(url_for('room_planner.index'))

    user = get_current_user()
    added_count = 0

    for pid_str in product_ids_raw:
        try:
            pid = int(pid_str)
            product = db.session.get(Product, pid)
            if not product or not product.is_active or product.stock <= 0:
                continue

            if user:
                cart_entry = CartItem.query.filter_by(user_id=user.id, product_id=product.id).first()
                if cart_entry:
                    if cart_entry.quantity < product.stock:
                        cart_entry.quantity += 1
                        added_count += 1
                else:
                    cart_entry = CartItem(user_id=user.id, product_id=product.id, quantity=1)
                    db.session.add(cart_entry)
                    added_count += 1
            else:
                guest_cart = session.get('guest_cart', {})
                current_qty = guest_cart.get(str(pid), 0)
                if current_qty < product.stock:
                    guest_cart[str(pid)] = current_qty + 1
                    session['guest_cart'] = guest_cart
                    added_count += 1
        except (ValueError, TypeError):
            continue

    if user:
        db.session.commit()

    flash(f"Success! Added {added_count} items from your room bundle to the cart.", "success")
    return redirect(url_for('cart.index'))
