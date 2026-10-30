# FurniSpace 🛋️

> A modern furniture e-commerce platform featuring new furniture shopping, a circular resale marketplace for pre-loved items, an intelligent "Complete My Room" budget-based bundle recommendation engine, and a dedicated administrative command center.

![FurniSpace Platform](https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80)

---

## 🌟 Core Features

### 1. Authentication & Role-Based Access Control (RBAC)
- **User Roles:** Customer and Administrator.
- **Dedicated Administrator Login:** Dedicated, secure admin portal (`/admin/login`) requiring manual entry of administrator email and password. Does not auto-login or use hardcoded credentials.
- **Secure Password Hashing:** Salted password hashing with Werkzeug (`scrypt`/`pbkdf2`). Passwords are never stored or compared in plain text.
- **Server-Side Route Guards:** Protected by `@login_required` and `@admin_required` decorators. Normal customers cannot access administrative endpoints by typing URLs directly.
- **Customer Protection:** Public registration strictly provisions `customer` accounts.

### 2. Furniture Shopping Catalogue
- **Curated Catalogue:** 24 realistic sample pieces across 8 categories: *Sofas, Beds, Tables, Chairs, Wardrobes, Storage, Lighting, and Decor*.
- **Verified Furniture Photography:** Every active product features a category-accurate, distinct photograph. Sofas display sofas, beds display beds, desks display desks, and armoires display armoires.
- **Resilient Fallback Image:** Local SVG fallback ensures clean visuals even if external networks are slow or offline.
- **Multi-Attribute Search & Filters:** Tokenized search by product name, description, material, category, style, and room suitability. Interactive category pills, price range presets, and style filters.
- **Sorting Options:** Featured, Price (Low to High), Price (High to Low), Newest additions, and Alphabetical.
- **Product Details:** High-resolution photography, dimension specifications, material details, and dynamic stock availability indicators.

### 3. Product Comparison
- **Side-by-Side Matrix:** Compare up to 3 furniture pieces simultaneously across price, category, material, colour, dimensions, room suitability, and stock status.
- **Enforced Limit:** Prevents layout breakage by restricting active comparisons to a maximum of 3 items.
- **Session Persistence:** Add, remove, or clear comparisons with instant badge counters across navigation.

### 4. Circular Resale Marketplace
- **Community Pre-Loved:** Peer-to-peer marketplace promoting sustainable, circular furniture lifecycles.
- **Photo Upload & Creation:** Registered customers can submit listings with title, category, description, asking price, condition (*Like New, Gently Used, Good, Fair*), location, contact info, and furniture photos.
- **Safe Image Uploads:** Validates file type and size on the server. Supports JPG, JPEG, PNG, and WEBP formats up to 16 MB with sanitized filenames. Features a live client-side preview.
- **Moderation Workflow:** All submissions start strictly as `Pending`. Only administrator-approved listings appear on the public marketplace.
- **Seller Transparency:** Sellers track their submission status (*Pending, Approved, Rejected*) and receive curator feedback directly in their dashboard.

### 5. "Complete My Room" Budget Bundle Engine
- **Deterministic Algorithm:** 100% mathematical Python recommendation engine without external AI API dependencies.
- **Guaranteed Budget Ceiling:** Select room type (*Living Room, Bedroom, Dining Room, Study Room*), target budget, and aesthetic style. The engine guarantees that the bundle cost **never exceeds** the budget.
- **Style Relaxation Communication:** When exact style matches are unaffordable within the specified budget, the algorithm gracefully relaxes style constraints while explaining the trade-off.
- **Interactive Swapping:** Swap any recommended piece with alternative options in the same category; totals and remaining budgets recalculate in real time.
- **One-Click Cart Addition:** Add the entire curated room bundle directly into the shopping cart.

### 6. Cart & Demo Checkout
- **Server-Side Validation:** Stock availability, quantities, and item subtotals are validated strictly on the server.
- **Atomic Transactions:** Order creation, order item price snapshots, stock deduction, and cart clearing execute within a single database transaction.
- **Demo Mode:** Clearly labeled simulated checkout requiring zero credit card details.
- **Order History:** Customers can review their past order receipts, while administrators update fulfillment stages (*Placed, Confirmed, Shipped, Delivered, Cancelled*) with stock restoration upon cancellation.

### 7. Administrative Command Center
- **Live Database Metrics:** Real-time metrics for registered customers, active inventory, lifetime demo orders, and pending resale listings.
- **Product Management:** Create new furniture products, adjust stock quantities on the fly, or toggle catalog visibility.
- **Order Lifecycle Management:** View order details and transition fulfillment statuses.
- **Resale Moderation Queue:** Approve or reject user-submitted resale listings with custom feedback notes.
- **Admin Session Control:** Dedicated admin logout securely ends administrative sessions.

---

## 🔑 Account Configuration & Demo Access

Administrator credentials and application secrets are configurable via environment variables:

```bash
# Optional: Configure Administrator Credentials
export ADMIN_USERNAME="admin"
export ADMIN_EMAIL="admin@furnispace.local"
export ADMIN_PASSWORD="<YourSecurePassword>"

# Optional: Configure Flask Secret Key and Port
export SECRET_KEY="<YourSecretKey>"
export PORT=5000
export HOST="0.0.0.0"
```

### Pre-Seeded Accounts for Evaluation

| Role | Username | Email | Portal / Entry Point |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin@furnispace.local` | `/admin/login` |
| **Customer 1** | `john_doe` | `john@example.com` | `/auth/login` |
| **Customer 2** | `sarah_m` | `sarah@example.com` | `/auth/login` |

*Note: For security best practices, passwords are authenticated using salted hashes in SQLite and can be updated through the database or environment variables.*

---

## 🚀 Setup & Local Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- `pip`

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/Atharva721/Furnispace.git
cd Furnispace
```

### 2. (Optional) Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your web browser.  
*The SQLite database is initialized and automatically seeded with accounts and 24 sample products upon first launch. Host is configured to `0.0.0.0` for full VS Code port forwarding compatibility.*

---

## 🧪 Automated Testing

FurniSpace includes a comprehensive pytest suite covering authentication, RBAC, dedicated admin login, photo upload validation, catalog filters, 3-item comparison limits, atomic checkout, stock reduction, resale moderation visibility, and budget bundle constraints:

```bash
python -m pytest -v
```

All 18 test scenarios pass with zero failures:
- `test_customer_registration`
- `test_login_logout`
- `test_customer_cannot_access_admin_portal`
- `test_dedicated_admin_login_success`
- `test_dedicated_admin_login_rejects_invalid_credentials`
- `test_dedicated_admin_login_rejects_normal_customer`
- `test_cart_and_checkout_flow`
- `test_order_history_isolation`
- `test_resale_submission_and_moderation_lifecycle`
- `test_resale_photo_upload_and_validation`
- `test_room_bundle_budget_constraint`
- `test_add_bundle_to_cart`
- `test_room_planner_render_recommendation`
- `test_shop_catalog_and_filtering`
- `test_product_detail`
- `test_product_comparison_limit`
- `test_advanced_search_and_price_filters`
- `test_all_products_have_valid_photos_and_accurate_categories`

---

## 📁 Repository Structure

```
FurniSpace/
├── app.py                  # Application factory, blueprints, port forwarding & error handlers
├── config.py               # Application configuration, uploads & secrets
├── models.py               # SQLAlchemy models (User, Product, CartItem, Order, OrderItem, ResaleListing)
├── seed.py                 # Initial database seeding and synchronization
├── recommendation.py       # Deterministic rule-based room budget algorithm
├── requirements.txt        # Python dependency manifest
├── routes/
│   ├── auth.py             # Login, register, logout & role decorators
│   ├── shop.py             # Catalogue, search, filters, details & comparison
│   ├── cart.py             # Cart operations, demo checkout & order history
│   ├── resale.py           # Community resale marketplace, photo uploads & submissions
│   ├── room_planner.py     # Complete My Room recommendation engine
│   └── admin.py            # Administrative portal, dedicated login & inventory controls
├── static/
│   ├── css/
│   │   └── style.css       # Warm organic design system
│   ├── js/
│   │   └── main.js         # Mobile navigation & image error fallbacks
│   ├── images/
│   │   └── fallback-furniture.svg # Local vector fallback image
│   └── uploads/            # Secure user-submitted resale photo uploads
├── templates/
│   ├── base.html           # Unified modern layout & navigation
│   ├── index.html          # Brand homepage & category showcase
│   ├── auth/               # Customer login & registration views
│   ├── shop/               # Catalogue, product detail & comparison table
│   ├── cart/               # Cart, checkout, confirmation & order history
│   ├── resale/             # Marketplace, photo upload form & seller dashboard
│   ├── room_planner/       # Room wizard & interactive bundle results
│   ├── admin/              # Dedicated login, dashboard, inventory, orders & resale moderation
│   └── errors/             # Custom 403, 404, and 500 error templates
└── tests/
    ├── conftest.py         # In-memory SQLite test fixtures
    ├── test_auth.py        # Dedicated admin login, RBAC & route protection
    ├── test_shop.py        # Catalogue search, filters, category integrity & comparison limits
    ├── test_cart_order.py  # Cart, atomic checkout & stock decrement
    ├── test_resale.py      # Resale photo upload, validation & moderation lifecycle
    └── test_room_planner.py# Budget ceiling guarantees & bundle-to-cart
```

---

## ⚖️ Academic & Demonstration Scope
- **Simulated Transactions:** Payment processing is simulated for demonstration purposes without real financial transactions.
- **Image Fallbacks:** Integrated SVG fallbacks guarantee layout integrity even if external CDNs are unreachable.
- **Data Persistence:** The local SQLite database persists in `instance/furnispace.db`. Stopping and restarting the server preserves all user data, orders, and listings.
