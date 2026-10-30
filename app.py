import os
from flask import Flask, render_template, session, g
from config import Config
from models import db, User, CartItem, ResaleListing
from seed import seed_database

# Blueprints
from routes.auth import auth_bp, get_current_user
from routes.shop import shop_bp
from routes.cart import cart_bp
from routes.resale import resale_bp
from routes.room_planner import room_planner_bp
from routes.admin import admin_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure uploads and instance directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(resale_bp)
    app.register_blueprint(room_planner_bp)
    app.register_blueprint(admin_bp)

    # Context processors for global template variables
    @app.context_processor
    def inject_global_data():
        user = get_current_user()
        
        # Calculate cart items count
        cart_count = 0
        if user:
            cart_count = sum(item.quantity for item in CartItem.query.filter_by(user_id=user.id).all())
        else:
            guest_cart = session.get('guest_cart', {})
            cart_count = sum(guest_cart.values())

        # Comparison count
        compare_count = len(session.get('compare_ids', []))

        # Admin pending alerts count
        pending_resale_count = 0
        if user and user.is_admin():
            pending_resale_count = ResaleListing.query.filter_by(status='Pending').count()

        return {
            'current_user': user,
            'cart_count': cart_count,
            'compare_count': compare_count,
            'pending_resale_count': pending_resale_count
        }

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Auto-seed initial tables and sample data if needed
    with app.app_context():
        seed_database(app)

    return app


app = create_app()

if __name__ == '__main__':
    # Accessible through VS Code port forwarding using appropriate host configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode by default when exposing the application
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host=host, port=port, debug=debug)
