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


def test_resale_photo_upload_and_validation(client, app):
    """Verifies that customers can upload valid image files (PNG/JPG), and invalid files are rejected."""
    import io

    # Log in customer
    client.post('/auth/login', data={
        'identifier': 'john_doe',
        'password': 'CustomerPass123!'
    }, follow_redirects=True)

    # 1. Test unsupported file format (.pdf)
    bad_file = (io.BytesIO(b"fake pdf content"), 'furniture_receipt.pdf')
    res_bad = client.post('/resale/submit', data={
        'title': 'Test Item Bad Format',
        'category': 'tables',
        'description': 'Description text here',
        'asking_price': '2500',
        'condition': 'Good',
        'location': 'Bangalore',
        'contact_info': 'john@example.com',
        'image_file': bad_file
    }, content_type='multipart/form-data', follow_redirects=True)
    assert res_bad.status_code == 200
    assert b"Unsupported image format" in res_bad.data

    # 2. Test valid image file (.png)
    png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    valid_file = (io.BytesIO(png_header), 'coffee_table.png')
    res_good = client.post('/resale/submit', data={
        'title': 'Solid Oak Nesting Coffee Table',
        'category': 'tables',
        'description': 'Stunning solid oak nesting tables, bought last year, selling due to move.',
        'asking_price': '4800',
        'condition': 'Like New',
        'location': 'Whitefield, Bangalore',
        'contact_info': '9876500000 | john@test.com',
        'image_file': valid_file
    }, content_type='multipart/form-data', follow_redirects=True)
    assert res_good.status_code == 200
    assert b"Your resale listing has been submitted" in res_good.data

    with app.app_context():
        uploaded_listing = ResaleListing.query.filter_by(title='Solid Oak Nesting Coffee Table').first()
        assert uploaded_listing is not None
        assert uploaded_listing.status == 'Pending'
        assert '/static/uploads/resale_' in uploaded_listing.image_url

    # 3. Test invalid price (<= 0)
    res_bad_price = client.post('/resale/submit', data={
        'title': 'Item with Invalid Price',
        'category': 'chairs',
        'description': 'Description text',
        'asking_price': '-500',
        'condition': 'Fair',
        'location': 'Delhi',
        'contact_info': 'seller@test.com',
        'image_url': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80'
    }, follow_redirects=True)
    assert b"Please enter a valid asking price greater than 0" in res_bad_price.data

    # 4. Test missing photo completely
    res_no_photo = client.post('/resale/submit', data={
        'title': 'Item without Photo',
        'category': 'chairs',
        'description': 'Description text',
        'asking_price': '1500',
        'condition': 'Good',
        'location': 'Delhi',
        'contact_info': 'seller@test.com',
        'image_url': ''
    }, follow_redirects=True)
    assert b"Please provide a furniture photograph" in res_no_photo.data

