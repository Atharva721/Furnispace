def test_customer_registration(client, app):
    """Verifies that a customer can register and public registration always assigns 'customer' role."""
    response = client.post('/auth/register', data={
        'username': 'newcustomer',
        'email': 'customer@furnispace.test',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'full_name': 'New Customer',
        'phone': '1234567890',
        'address': 'Test City'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        from models import User
        user = User.query.filter_by(username='newcustomer').first()
        assert user is not None
        assert user.role == 'customer'  # Must be customer
        assert user.check_password('Password123!') is True


def test_login_logout(client):
    """Verifies customer login and logout."""
    # Login with seeded customer
    res = client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back" in res.data

    # Logout
    res = client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b"signed out successfully" in res.data


def test_customer_cannot_access_admin_portal(client):
    """Customer role cannot access /admin/ routes and receives 403 or redirect."""
    # Log in as customer
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    res = client.get('/admin/', follow_redirects=False)
    assert res.status_code in [302, 403]

    res_followed = client.get('/admin/', follow_redirects=True)
    assert b"Administrator privileges required" in res_followed.data or res_followed.status_code == 403


def test_admin_access_allowed(client):
    """Admin can log in and successfully load /admin/ dashboard."""
    client.post('/auth/login', data={
        'identifier': 'admin',
        'password': 'AdminPassword123!'
    }, follow_redirects=True)

    res = client.get('/admin/', follow_redirects=True)
    assert res.status_code == 200
    assert b"Overview Dashboard" in res.data
    assert b"Administrative Portal" in res.data
