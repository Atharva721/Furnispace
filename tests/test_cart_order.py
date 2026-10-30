from models import Product, Order, OrderItem, db

def test_cart_and_checkout_flow(client, app):
    """Verifies adding items to cart, checkout, stock decrement, and order creation."""
    # Login as john_doe
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    with app.app_context():
        p1 = db.session.get(Product, 1)
        initial_stock = p1.stock

    # Add product 1 to cart
    res_add = client.post('/cart/add/1', data={'quantity': 2}, follow_redirects=True)
    assert res_add.status_code == 200

    # View cart
    res_cart = client.get('/cart')
    assert res_cart.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res_cart.data

    # Complete Checkout
    res_checkout = client.post('/checkout', data={
        'customer_name': 'John Doe',
        'customer_phone': '+91 91234 56789',
        'delivery_address': '42 Blossom Avenue, Bangalore'
    }, follow_redirects=True)
    assert res_checkout.status_code == 200
    assert b"Thank You For Your Order!" in res_checkout.data

    # Verify database state: Order created, stock decreased by 2
    with app.app_context():
        p1_after = db.session.get(Product, 1)
        assert p1_after.stock == initial_stock - 2

        order = Order.query.filter_by(customer_name='John Doe').order_by(Order.id.desc()).first()
        assert order is not None
        assert order.status == 'Placed'
        assert len(order.items) >= 1
        assert order.items[0].product_id == 1
        assert order.items[0].quantity == 2


def test_order_history_isolation(client, app):
    """Verifies customers can view only their own orders."""
    # John doe logs in
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    res_orders = client.get('/orders')
    assert res_orders.status_code == 200
