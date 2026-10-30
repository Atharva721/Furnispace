# FurniSpace 🛋️

> A modern furniture e-commerce platform featuring new furniture shopping, a circular resale marketplace for pre-loved items, and an intelligent "Complete My Room" budget-based bundle recommendation engine.

![FurniSpace Platform](https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80)

---

## 🌟 Core Features

### 1. Authentication & Role-Based Access Control (RBAC)
- **User Roles:** Customer and Administrator.
- **Secure Credentials:** Strong password hashing with Werkzeug (`scrypt`/`pbkdf2`).
- **Route Guards:** Server-side decorators `@login_required` and `@admin_required`. Non-admins cannot access admin portals.
- **Customer Protection:** Public registration strictly provisions `customer` accounts.

### 2. New Furniture Shop
- **Curated Catalogue:** 24 realistic sample pieces across 8 categories: *Sofas, Beds, Tables, Chairs, Wardrobes, Storage, Lighting, and Decor*.
- **Search & Filters:** Search by keywords, filter by category, price ranges, and aesthetic styles (*Modern, Minimalist, Traditional, Contemporary*).
- **Sorting Options:** Featured, Price (Low to High), Price (High to Low), Newest additions, and Alphabetical.
- **Product Details:** High-resolution photography, dimension specs, material details, and dynamic stock availability indicators.

### 3. Product Comparison
- **Side-by-Side Matrix:** Compare up to 3 furniture pieces simultaneously across price, category, material, colour, dimensions, room suitability, and availability.
- **Enforced Limit:** Protects layout readability by preventing comparison of more than 3 products.
- **Session Management:** Add, remove, or clear comparisons with instant badge counters.

### 4. Circular Resale Marketplace
- **Community Pre-Loved:** Peer-to-peer marketplace promoting sustainable, circular furniture lifecycles.
- **Listing Submission:** Logged-in customers can submit furniture with title, category, description, asking price, condition (*Like New, Gently Used, Good, Fair*), location, contact info, and photos.
- **Moderation Workflow:** All submissions start strictly as `Pending`. Only `Approved` listings appear on the public marketplace.
- **Seller Transparency:** Sellers track their submission status (*Pending, Approved, Rejected*) and receive curator feedback.

### 5. "Complete My Room" Budget Bundle Engine
- **Deterministic Algorithm:** 100% mathematical Python recommendation engine without external AI API dependencies.
- **Guaranteed Budget Ceiling:** Select room type (*Living Room, Bedroom, Dining Room, Study Room*), target budget, and aesthetic style. The engine guarantees that the bundle cost **never exceeds** the budget.
- **Interactive Swapping:** Swap any recommended piece with alternative options in the same category; totals and remaining budgets recalculate in real time.
- **One-Click Cart Addition:** Add the entire curated room bundle directly into the shopping cart.

### 6. Cart & Demo Checkout
- **Server-Side Validation:** Stock availability and item subtotals are validated strictly on the server.
- **Atomic Transactions:** Order creation, order item snapshots, stock deduction, and cart clearing execute within a single database transaction.
- **Demo Mode:** Clearly labeled simulated checkout requiring zero credit card details.
- **Order History:** Customers can review their past order receipts, while administrators update fulfillment stages (*Placed, Confirmed, Shipped, Delivered, Cancelled*).

### 7. Administrative Command Center
- **Live Metrics:** Real-time database metrics for total customers, active inventory, lifetime demo orders, and pending resale listings.
- **Inventory Control:** Create new furniture products, adjust stock quantities on the fly, or toggle catalog visibility.
- **Order Lifecycle Management:** View and transition order statuses with automated stock restoration upon order cancellation.
- **Moderation Queue:** Approve or reject user-submitted resale listings with custom feedback notes.

---

## 🔑 Demo Credentials

| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin@furnispace.local` | `AdminPassword123!` |
| **Customer 1** | `john_doe` | `john@example.com` | `CustomerPass123!` |
| **Customer 2** | `sarah_m` | `sarah@example.com` | `CustomerPass123!` |

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
*The SQLite database is initialized and automatically seeded with admin accounts and 24 sample products upon first launch.*

---

## 🧪 Automated Testing

FurniSpace includes a comprehensive pytest suite covering authentication, RBAC, catalog filters, 3-item comparison limits, atomic checkout, stock reduction, resale moderation visibility, and budget bundle constraints:

```bash
python -m pytest -v
```

All 12 test scenarios pass with zero failures.

---

## 📁 Repository Structure

```
FurniSpace/
├── app.py                  # Application factory, blueprints & context processors
├── config.py               # Application configuration & secrets
├── models.py               # SQLAlchemy models (User, Product, CartItem, Order, OrderItem, ResaleListing)
├── seed.py                 # Initial database seeding script
├── recommendation.py       # Deterministic rule-based room budget algorithm
├── requirements.txt        # Python dependency manifest
├── routes/
│   ├── auth.py             # Login, register, logout & role decorators
│   ├── shop.py             # Catalogue, search, filters, details & comparison
│   ├── cart.py             # Cart operations, demo checkout & order history
│   ├── resale.py           # Community resale marketplace & listing submissions
│   ├── room_planner.py     # Complete My Room recommendation engine
│   └── admin.py            # Administrative dashboard & inventory management
├── static/
│   ├── css/
│   │   └── style.css       # Warm organic design system
│   └── js/
│       └── main.js         # Mobile navigation & image fallbacks
├── templates/
│   ├── base.html           # Unified modern layout & navigation
│   ├── index.html          # Brand homepage & category showcase
│   ├── auth/               # Login & registration views
│   ├── shop/               # Catalogue, product detail & comparison table
│   ├── cart/               # Cart, checkout, confirmation & order history
│   ├── resale/             # Marketplace, submission form & seller dashboard
│   ├── room_planner/       # Room wizard & interactive bundle results
│   ├── admin/              # Dashboard, inventory, orders & resale moderation
│   └── errors/             # Custom 403, 404, and 500 error templates
└── tests/
    ├── conftest.py         # In-memory SQLite test fixtures
    ├── test_auth.py        # Registration, login & admin route protection
    ├── test_shop.py        # Catalogue search, filters & comparison limits
    ├── test_cart_order.py  # Cart, atomic checkout & stock decrement
    ├── test_resale.py      # Resale moderation & visibility lifecycle
    └── test_room_planner.py# Budget ceiling guarantees & bundle-to-cart
```

---

## ⚖️ Academic & Demonstration Scope
- **Simulated Transactions:** Payment processing is simulated for demonstration purposes without real financial transactions.
- **Image Fallbacks:** Integrated SVG data-URI fallbacks guarantee layout integrity even if external CDNs are unreachable.
- **Data Persistence:** The local SQLite database persists in `instance/furnispace.db`. Stopping and restarting the server preserves all user data, orders, and listings.
