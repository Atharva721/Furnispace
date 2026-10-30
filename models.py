from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

def utc_now():
    return datetime.now(timezone.utc)

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer', nullable=False)  # 'customer' or 'admin'
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    cart_items = db.relationship('CartItem', backref='user', cascade='all, delete-orphan', lazy=True)
    orders = db.relationship('Order', backref='user', cascade='all, delete-orphan', lazy=True)
    resale_listings = db.relationship('ResaleListing', backref='seller', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # sofas, beds, tables, chairs, wardrobes, storage, lighting, decor
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Stored in whole currency units (e.g. ₹ / $)
    material = db.Column(db.String(100), default='Solid Wood')
    colour = db.Column(db.String(50), default='Natural')
    dimensions = db.Column(db.String(100), default='Standard')
    stock = db.Column(db.Integer, default=10, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    room_types = db.Column(db.String(200), default='Living Room')  # Comma-separated: "Living Room,Bedroom"
    style = db.Column(db.String(50), default='Modern', index=True)  # Modern, Minimalist, Traditional, Contemporary
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def in_stock(self):
        return self.stock > 0

    def room_list(self):
        return [r.strip() for r in self.room_types.split(',') if r.strip()]

    def __repr__(self):
        return f"<Product {self.name} (Stock: {self.stock})>"


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    product = db.relationship('Product', backref='cart_entries')

    @property
    def subtotal(self):
        if self.product:
            return self.product.price * self.quantity
        return 0

    def __repr__(self):
        return f"<CartItem User:{self.user_id} Product:{self.product_id} Qty:{self.quantity}>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default='Placed', nullable=False)  # Placed, Confirmed, Shipped, Delivered, Cancelled
    created_at = db.Column(db.DateTime, default=utc_now)

    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Order {self.order_number} ({self.status})>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)
    product_name = db.Column(db.String(150), nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)  # Price snapshot at order time
    quantity = db.Column(db.Integer, default=1, nullable=False)

    product = db.relationship('Product')

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __repr__(self):
        return f"<OrderItem {self.product_name} x {self.quantity}>"


class ResaleListing(db.Model):
    __tablename__ = 'resale_listings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    asking_price = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # Like New, Gently Used, Good, Fair
    location = db.Column(db.String(120), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # Pending, Approved, Rejected
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f"<ResaleListing {self.title} ({self.status})>"
