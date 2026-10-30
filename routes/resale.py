import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import db, ResaleListing
from routes.auth import get_current_user, login_required

resale_bp = Blueprint('resale', __name__, url_prefix='/resale')

RESALE_CATEGORIES = [
    ('all', 'All Categories'),
    ('sofas', 'Sofas & Seating'),
    ('beds', 'Beds & Mattresses'),
    ('tables', 'Tables & Desks'),
    ('chairs', 'Chairs'),
    ('wardrobes', 'Wardrobes & Closets'),
    ('storage', 'Storage & Shelving'),
    ('lighting', 'Lighting'),
    ('decor', 'Decor & Rugs')
]

CONDITIONS = ['Like New', 'Gently Used', 'Good', 'Fair']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@resale_bp.route('/')
def index():
    """Public marketplace: Only displays listings with status 'Approved'."""
    category = request.args.get('category', 'all').lower()
    search_query = request.args.get('q', '').strip()
    condition = request.args.get('condition', '')
    max_price = request.args.get('max_price', type=int)

    # CRITICAL: Always filter by status == 'Approved'
    query = ResaleListing.query.filter_by(status='Approved')

    if category and category != 'all':
        query = query.filter(ResaleListing.category == category)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (ResaleListing.title.ilike(search_pattern)) |
            (ResaleListing.description.ilike(search_pattern)) |
            (ResaleListing.location.ilike(search_pattern))
        )

    if condition:
        query = query.filter(ResaleListing.condition == condition)

    if max_price is not None:
        query = query.filter(ResaleListing.asking_price <= max_price)

    listings = query.order_by(ResaleListing.created_at.desc()).all()

    return render_template(
        'resale/index.html',
        listings=listings,
        categories=RESALE_CATEGORIES,
        conditions=CONDITIONS,
        current_category=category,
        search_query=search_query,
        current_condition=condition,
        max_price=max_price
    )


@resale_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    """Customer submits a pre-loved furniture listing. Defaults strictly to 'Pending'."""
    user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip().lower()
        description = request.form.get('description', '').strip()
        price_raw = request.form.get('asking_price', '').strip()
        condition = request.form.get('condition', '').strip()
        location = request.form.get('location', '').strip()
        contact_info = request.form.get('contact_info', '').strip()
        image_url = request.form.get('image_url', '').strip()

        form_data = {
            'title': title,
            'category': category,
            'description': description,
            'asking_price': price_raw,
            'condition': condition,
            'location': location,
            'contact_info': contact_info,
            'image_url': image_url
        }

        # Validate mandatory text fields
        if not title or not category or not description or not location or not contact_info:
            flash("Please complete all required listing fields.", "danger")
            return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data=form_data)

        # Validate asking price
        try:
            asking_price = int(price_raw)
            if asking_price <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            flash("Please enter a valid asking price greater than 0.", "danger")
            return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data=form_data)

        # Validate and handle image upload or URL
        final_image_url = image_url
        has_file = 'image_file' in request.files and request.files['image_file'].filename

        if has_file:
            file = request.files['image_file']
            if not allowed_file(file.filename):
                flash("Unsupported image format. Allowed formats are JPG, JPEG, PNG, and WEBP.", "danger")
                return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data=form_data)

            try:
                raw_filename = secure_filename(file.filename)
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                if not raw_filename:
                    raw_filename = f"upload.{ext}"
                unique_name = f"resale_{uuid.uuid4().hex[:10]}_{raw_filename}"
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, unique_name)
                file.save(file_path)
                final_image_url = url_for('static', filename=f"uploads/{unique_name}")
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", "danger")
                return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data=form_data)

        # Ensure a furniture photograph is provided
        if not final_image_url:
            flash("Please provide a furniture photograph by uploading a photo or entering an image link.", "danger")
            return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data=form_data)

        # Create listing with status strictly 'Pending'
        new_listing = ResaleListing(
            user_id=user.id,
            title=title,
            category=category,
            description=description,
            asking_price=asking_price,
            condition=condition or 'Gently Used',
            location=location,
            contact_info=contact_info,
            image_url=final_image_url,
            status='Pending'  # Always Pending initially
        )
        db.session.add(new_listing)
        db.session.commit()

        flash("Your resale listing has been submitted! It is now Pending review by our moderation team.", "success")
        return redirect(url_for('resale.my_listings'))

    return render_template('resale/submit.html', categories=RESALE_CATEGORIES, conditions=CONDITIONS, form_data={})


@resale_bp.route('/my-listings')
@login_required
def my_listings():
    """Displays all listings submitted by the currently authenticated customer."""
    user = get_current_user()
    user_listings = ResaleListing.query.filter_by(user_id=user.id).order_by(ResaleListing.created_at.desc()).all()
    return render_template('resale/my_listings.html', listings=user_listings)
