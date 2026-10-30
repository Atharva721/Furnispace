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
    """Customer role cannot access /admin/ routes and receives 403."""
    # Log in as customer
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    res = client.get('/admin/', follow_redirects=False)
    assert res.status_code == 403 or (res.status_code == 302 and '/admin' not in res.location)

    res_followed = client.get('/admin/', follow_redirects=True)
    assert res_followed.status_code == 403 or b"Administrator privileges required" in res_followed.data


def test_dedicated_admin_login_success(client):
    """Administrator enters email and password on dedicated /admin/login page and gains access."""
    # GET renders page
    res_get = client.get('/admin/login')
    assert res_get.status_code == 200
    assert b"Administrator Login" in res_get.data
    assert b"admin@furnispace.local" in res_get.data

    # POST with valid admin credentials
    res_post = client.post('/admin/login', data={
        'email': 'admin@furnispace.local',
        'password': 'AdminPassword123!'
    }, follow_redirects=True)
    assert res_post.status_code == 200
    assert b"Overview Dashboard" in res_post.data
    assert b"Administrative Portal" in res_post.data

    # Admin Logout
    res_logout = client.get('/admin/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"Administrator session ended successfully" in res_logout.data


def test_dedicated_admin_login_rejects_invalid_credentials(client):
    """Dedicated /admin/login rejects incorrect passwords or unknown emails."""
    # Unknown email
    res1 = client.post('/admin/login', data={
        'email': 'nonexistent@furnispace.local',
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert res1.status_code == 200
    assert b"Administrator account not found" in res1.data

    # Wrong password for existing admin
    res2 = client.post('/admin/login', data={
        'email': 'admin@furnispace.local',
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert res2.status_code == 200
    assert b"Invalid administrator credentials" in res2.data


def test_dedicated_admin_login_rejects_normal_customer(client):
    """Dedicated /admin/login rejects accounts that do not have administrator role."""
    res = client.post('/admin/login', data={
        'email': 'john@example.com',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"This account does not possess administrator privileges" in res.data

