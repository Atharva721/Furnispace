from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, User, CartItem

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_current_user():
    """Retrieves current authenticated user from session or g."""
    if 'user_id' not in session:
        return None
    if not hasattr(g, 'current_user') or g.current_user is None:
        g.current_user = db.session.get(User, session['user_id'])
    return g.current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash("Admin authentication required.", "danger")
            return redirect(url_for('auth.login', next=request.url))
        if not user.is_admin():
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for('shop.index')), 403
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if get_current_user():
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        # Server-side validation
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template('auth/register.html')

        if not email or '@' not in email:
            flash("A valid email address is required.", "danger")
            return render_template('auth/register.html')

        if not password or len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('auth/register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/register.html')

        # Check existing username/email
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' is already taken.", "danger")
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash(f"An account with email '{email}' already exists.", "danger")
            return render_template('auth/register.html')

        # Always assign role 'customer' for public registration
        new_user = User(
            username=username,
            email=email,
            role='customer',
            full_name=full_name or username.title(),
            phone=phone,
            address=address
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please sign in with your credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user():
        return redirect(url_for('shop.index'))

    next_url = request.args.get('next')

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next') or next_url

        if not identifier or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template('auth/login.html', next=next_url)

        # Allow logging in with either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash(f"Welcome back, {user.full_name or user.username}!", "success")

            # Route admin directly to admin dashboard if logging in without a specific next destination
            if user.is_admin() and (not next_url or next_url == url_for('shop.index')):
                return redirect(url_for('admin.dashboard'))

            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('shop.index'))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template('auth/login.html', next=next_url)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    g.current_user = None
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('shop.index'))
