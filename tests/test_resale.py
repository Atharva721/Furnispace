from models import ResaleListing, db

def test_resale_submission_and_moderation_lifecycle(client, app):
    """
    Verifies that:
    1. Newly submitted listing starts as 'Pending'
    2. Pending listing is NOT shown on the public marketplace
    3. Admin approves listing -> becomes visible on public marketplace
    4. Admin rejects listing -> remains hidden from public marketplace
    """
    # 1. Login as customer
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    # Submit listing
    res_sub = client.post('/resale/submit', data={
        'title': 'Minimalist Ash Study Desk',
        'category': 'tables',
        'description': 'Used for 4 months, pristine condition without scratches.',
        'asking_price': 5500,
        'condition': 'Like New',
        'location': 'Koramangala, Bangalore',
        'contact_info': 'john.test@example.com',
        'image_url': 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&w=800&q=80'
    }, follow_redirects=True)
    assert res_sub.status_code == 200

    with app.app_context():
        new_item = ResaleListing.query.filter_by(title='Minimalist Ash Study Desk').first()
        assert new_item is not None
        assert new_item.status == 'Pending'  # Must be Pending
        listing_id = new_item.id

    # 2. Check public marketplace: must NOT appear while Pending
    res_pub = client.get('/resale/')
    assert b"Minimalist Ash Study Desk" not in res_pub.data

    # 3. Log out customer, log in as admin to moderate
    client.get('/auth/logout')
    client.post('/auth/login', data={
        'identifier': 'admin',
        'password': 'AdminPassword123!'
    }, follow_redirects=True)

    # Admin approves listing
    res_approve = client.post(f'/admin/resale/moderate/{listing_id}', data={
        'action': 'approve',
        'admin_notes': 'Verified condition and fair price.'
    }, follow_redirects=True)
    assert res_approve.status_code == 200

    with app.app_context():
        approved_item = db.session.get(ResaleListing, listing_id)
        assert approved_item.status == 'Approved'

    # Now check public marketplace: must be visible!
    res_pub_approved = client.get('/resale/')
    assert b"Minimalist Ash Study Desk" in res_pub_approved.data

    # 4. Now test Rejection
    # Customer submits a second listing
    client.get('/auth/logout')
    client.post('/auth/login', data={
        'identifier': 'sarah_m',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    client.post('/resale/submit', data={
        'title': 'Broken Chair For Parts',
        'category': 'chairs',
        'description': 'Leg cracked, wobbly.',
        'asking_price': 300,
        'condition': 'Fair',
        'location': 'Pune',
        'contact_info': 'sarah@example.com',
        'image_url': 'https://images.unsplash.com/photo-1580481077197-0335e23970b8?auto=format&fit=crop&w=800&q=80'
    }, follow_redirects=True)

    with app.app_context():
        broken_item = ResaleListing.query.filter_by(title='Broken Chair For Parts').first()
        broken_id = broken_item.id

    # Admin logs in and rejects
    client.get('/auth/logout')
    client.post('/auth/login', data={
        'identifier': 'admin',
        'password': 'AdminPassword123!'
    }, follow_redirects=True)

    client.post(f'/admin/resale/moderate/{broken_id}', data={
        'action': 'reject',
        'admin_notes': 'Damaged items cannot be listed.'
    }, follow_redirects=True)

    # Public marketplace: must NOT show rejected item
    res_pub_rejected = client.get('/resale/')
    assert b"Broken Chair For Parts" not in res_pub_rejected.data
