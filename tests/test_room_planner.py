from recommendation import recommend_room_bundle
from models import CartItem

def test_room_bundle_budget_constraint(app):
    """
    Verifies that the recommendation algorithm strictly guarantees total <= budget
    across different rooms and budgets.
    """
    with app.app_context():
        # Test 1: Standard budget
        bundle1 = recommend_room_bundle(room_type='Living Room', budget=60000, style='Modern')
        assert bundle1['success'] is True
        assert bundle1['total_price'] <= 60000
        assert bundle1['remaining_budget'] >= 0
        assert len(bundle1['items']) >= 2

        # Test 2: Bedroom bundle
        bundle2 = recommend_room_bundle(room_type='Bedroom', budget=55000, style='Minimalist')
        assert bundle2['success'] is True
        assert bundle2['total_price'] <= 55000
        assert bundle2['remaining_budget'] >= 0

        # Test 3: Unattainable budget (e.g. ₹500 for a whole living room)
        bundle_low = recommend_room_bundle(room_type='Living Room', budget=500, style='Modern')
        assert bundle_low['success'] is False
        assert bundle_low['total_price'] == 0


def test_add_bundle_to_cart(client, app):
    """Verifies that an entire recommended bundle can be added to the cart."""
    # Login as customer
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    # Post add_bundle with product IDs 1 and 7
    res = client.post('/room-planner/add-bundle', data={
        'product_ids': ['1', '7']
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Added 2 items from your room bundle" in res.data

    # Verify cart has both products
    res_cart = client.get('/cart')
    assert res_cart.status_code == 200
    assert b"Nordic Velvet 3-Seater Sofa" in res_cart.data
    assert b"Svalbard Extendable Dining Table" in res_cart.data


def test_room_planner_render_recommendation(client):
    """Verifies that /room-planner/recommend renders successfully via both GET and POST."""
    # POST
    res_post = client.post('/room-planner/recommend', data={
        'room_type': 'Living Room',
        'budget': 65000,
        'style': 'Modern'
    })
    assert res_post.status_code == 200
    assert b"Your Modern Living Room Bundle" in res_post.data
    assert b"Target Budget" in res_post.data

    # GET
    res_get = client.get('/room-planner/recommend?room_type=Bedroom&budget=70000&style=Minimalist')
    assert res_get.status_code == 200
    assert b"Your Minimalist Bedroom Bundle" in res_get.data

