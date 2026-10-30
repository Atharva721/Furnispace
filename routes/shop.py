from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Product

shop_bp = Blueprint('shop', __name__)

CATEGORIES = [
    ('all', 'All Furniture'),
    ('sofas', 'Sofas & Couches'),
    ('beds', 'Beds & Mattresses'),
    ('tables', 'Tables & Desks'),
    ('chairs', 'Chairs & Benches'),
    ('wardrobes', 'Wardrobes & Closets'),
    ('storage', 'Storage & Credenzas'),
    ('lighting', 'Lamps & Lighting'),
    ('decor', 'Rugs & Decor')
]

STYLES = ['Modern', 'Minimalist', 'Traditional', 'Contemporary']


@shop_bp.route('/')
def home():
    """Homepage showcasing brand narrative, categories, and featured products."""
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()
    categories_summary = [c for c in CATEGORIES if c[0] != 'all']
    return render_template(
        'index.html',
        featured_products=featured_products,
        categories=categories_summary
    )


@shop_bp.route('/shop')
def index():
    """Product catalog with search, category filtering, price filtering and sorting."""
    category = request.args.get('category', 'all').lower()
    search_query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    style = request.args.get('style', '')
    sort_by = request.args.get('sort', 'featured')

    query = Product.query.filter(Product.is_active.is_(True))

    if category and category != 'all':
        query = query.filter(Product.category == category)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) | 
            (Product.description.ilike(search_pattern)) |
            (Product.material.ilike(search_pattern))
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if style and style != 'All':
        query = query.filter(Product.style == style)

    # Sorting
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        # Default featured ordering
        query = query.order_by(Product.stock.desc(), Product.id.asc())

    products = query.all()
    compare_ids = session.get('compare_ids', [])

    return render_template(
        'shop/index.html',
        products=products,
        categories=CATEGORIES,
        styles=STYLES,
        current_category=category,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        current_style=style,
        current_sort=sort_by,
        compare_ids=compare_ids
    )


@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Detailed view for a specific furniture product."""
    product = Product.query.get_or_404(product_id)
    if not product.is_active:
        flash("This product is currently unavailable.", "warning")
        return redirect(url_for('shop.index'))

    # Suggested related products from same category or style
    related_products = Product.query.filter(
        Product.id != product.id,
        Product.is_active.is_(True),
        Product.category == product.category
    ).limit(3).all()

    compare_ids = session.get('compare_ids', [])
    is_in_compare = product.id in compare_ids

    return render_template(
        'shop/detail.html',
        product=product,
        related_products=related_products,
        is_in_compare=is_in_compare
    )


# --- PRODUCT COMPARISON (Up to 3 products) ---

@shop_bp.route('/compare')
def compare():
    """Side-by-side comparison page for up to 3 selected products."""
    compare_ids = session.get('compare_ids', [])
    products = Product.query.filter(
        Product.id.in_(compare_ids),
        Product.is_active.is_(True)
    ).all() if compare_ids else []

    # Preserve order of selection
    ordered_products = []
    prod_map = {p.id: p for p in products}
    for pid in compare_ids:
        if pid in prod_map:
            ordered_products.append(prod_map[pid])

    return render_template('shop/compare.html', products=ordered_products)


@shop_bp.route('/compare/add/<int:product_id>', methods=['POST', 'GET'])
def compare_add(product_id):
    """Adds a product to comparison list, enforcing the 3-item maximum constraint."""
    product = Product.query.get_or_404(product_id)
    compare_ids = session.get('compare_ids', [])

    if product_id in compare_ids:
        flash(f"'{product.name}' is already in your comparison list.", "info")
    elif len(compare_ids) >= 3:
        flash("You can compare up to 3 products at a time. Please remove an item first.", "warning")
    else:
        compare_ids.append(product_id)
        session['compare_ids'] = compare_ids
        flash(f"Added '{product.name}' to comparison.", "success")

    redirect_to = request.referrer or url_for('shop.compare')
    return redirect(redirect_to)


@shop_bp.route('/compare/remove/<int:product_id>', methods=['POST', 'GET'])
def compare_remove(product_id):
    """Removes a product from the comparison list."""
    compare_ids = session.get('compare_ids', [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        session['compare_ids'] = compare_ids
        flash("Item removed from comparison.", "info")

    return redirect(url_for('shop.compare'))


@shop_bp.route('/compare/clear', methods=['POST', 'GET'])
def compare_clear():
    """Clears all products from comparison."""
    session['compare_ids'] = []
    flash("Comparison list cleared.", "info")
    return redirect(url_for('shop.compare'))
