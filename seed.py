"""
Seed script for FurniSpace.
Populates:
1. Demo Admin account and Customer test accounts
2. At least 24 realistic furniture products across 8 categories
3. Initial Resale listings with varied statuses (Pending, Approved, Rejected)
"""

from models import db, User, Product, ResaleListing

SAMPLE_PRODUCTS = [
    # SOFAS
    {
        "name": "Nordic Velvet 3-Seater Sofa",
        "category": "sofas",
        "description": "Plush 3-seater sofa with high-density foam cushioning, kiln-dried solid beech frame, and stain-resistant velvet upholstery.",
        "price": 24999,
        "material": "Velvet & Solid Beech",
        "colour": "Forest Olive",
        "dimensions": "W 215cm x D 92cm x H 84cm",
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Study Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Artisan Linen Modular Sectional",
        "category": "sofas",
        "description": "Versatile L-shaped sectional featuring breathable organic linen covers, feather-blend cushions, and deep lounge seating.",
        "price": 38999,
        "material": "Organic Linen & Pine",
        "colour": "Oatmeal Beige",
        "dimensions": "W 270cm x D 165cm x H 80cm",
        "stock": 5,
        "image_url": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room",
        "style": "Contemporary",
        "is_active": True
    },
    {
        "name": "Classic Chesterfield Leather Couch",
        "category": "sofas",
        "description": "Deep button-tufted top-grain leather sofa with scroll arms and hand-turned walnut feet. An enduring heirloom centerpiece.",
        "price": 45999,
        "material": "Top-Grain Leather & Walnut",
        "colour": "Cognac Brown",
        "dimensions": "W 220cm x D 95cm x H 78cm",
        "stock": 4,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Study Room",
        "style": "Traditional",
        "is_active": True
    },

    # BEDS
    {
        "name": "Kobenhavn Solid Oak Platform Bed",
        "category": "beds",
        "description": "Minimalist low-profile platform bed crafted from sustainably sourced European white oak with floating headboard profile.",
        "price": 28999,
        "material": "Solid White Oak",
        "colour": "Natural Oak",
        "dimensions": "W 160cm x L 208cm x H 90cm",
        "stock": 6,
        "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Minimalist",
        "is_active": True
    },
    {
        "name": "Verona Upholstered King Bed",
        "category": "beds",
        "description": "Generously padded tailored fabric headboard with horizontal channeling and reinforced slat support system.",
        "price": 32499,
        "material": "Textured Weave & Solid Pine",
        "colour": "Charcoal Grey",
        "dimensions": "W 190cm x L 215cm x H 115cm",
        "stock": 7,
        "image_url": "https://images.unsplash.com/photo-1540518614846-7ede433c4b18?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Heritage Carved Sheesham Bed",
        "category": "beds",
        "description": "Handcrafted Indian rosewood queen bed with delicate lattice detailing and traditional honey gloss finish.",
        "price": 26999,
        "material": "Solid Sheesham Wood",
        "colour": "Warm Amber",
        "dimensions": "W 165cm x L 210cm x H 105cm",
        "stock": 5,
        "image_url": "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Traditional",
        "is_active": True
    },

    # TABLES
    {
        "name": "Svalbard Extendable Dining Table",
        "category": "tables",
        "description": "Seats 6 to 10 with an effortless butterfly extension mechanism. Solid ash veneer over engineered birch core.",
        "price": 18999,
        "material": "Ash Veneer & Birch Core",
        "colour": "Pale Ash",
        "dimensions": "L 180-240cm x W 90cm x H 75cm",
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80",
        "room_types": "Dining Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Aalto Round Glass & Walnut Dining Table",
        "category": "tables",
        "description": "Tempered architectural glass tabletop set upon a sculptural cross-leg solid walnut base. Perfect for intimate spaces.",
        "price": 16499,
        "material": "Tempered Glass & Solid Walnut",
        "colour": "Dark Walnut / Clear",
        "dimensions": "Dia 120cm x H 76cm",
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?auto=format&fit=crop&w=800&q=80",
        "room_types": "Dining Room,Living Room",
        "style": "Contemporary",
        "is_active": True
    },
    {
        "name": "Oslo Minimalist Writing Desk",
        "category": "tables",
        "description": "Streamlined home-office desk with integrated dual cable management grommets and a concealed felt-lined stationery drawer.",
        "price": 11999,
        "material": "Solid Birch & Matte Powder Steel",
        "colour": "Matte Black & Natural Birch",
        "dimensions": "W 120cm x D 60cm x H 75cm",
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&w=800&q=80",
        "room_types": "Study Room,Bedroom",
        "style": "Minimalist",
        "is_active": True
    },

    # CHAIRS
    {
        "name": "Scandi Ergonomic Wishbone Chairs (Set of 2)",
        "category": "chairs",
        "description": "Iconic Y-back steam-bent solid beech frame paired with hand-woven natural paper cord seating. Exceptional lumbar support.",
        "price": 8999,
        "material": "Solid Beech & Paper Cord",
        "colour": "Natural Beech",
        "dimensions": "W 55cm x D 52cm x H 76cm",
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1580481077197-0335e23970b8?auto=format&fit=crop&w=800&q=80",
        "room_types": "Dining Room,Study Room",
        "style": "Minimalist",
        "is_active": True
    },
    {
        "name": "Modena Swivel Executive Desk Chair",
        "category": "chairs",
        "description": "High-back desk chair wrapped in supple vegan leather with synchronous tilt tension mechanism and nylon caster wheels.",
        "price": 13499,
        "material": "Vegan Leather & Brushed Aluminium",
        "colour": "Saddle Tan",
        "dimensions": "W 65cm x D 65cm x H 105-115cm",
        "stock": 9,
        "image_url": "https://images.unsplash.com/photo-1580481077197-0335e23970b8?auto=format&fit=crop&w=800&q=80",
        "room_types": "Study Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Boucle Accent Lounge Armchair",
        "category": "chairs",
        "description": "Sculptural curved armchair upholstered in tactile cream bouclé fabric with blackened tubular steel legs.",
        "price": 12999,
        "material": "Cream Bouclé & Steel",
        "colour": "Ivory Cream",
        "dimensions": "W 78cm x D 75cm x H 76cm",
        "stock": 11,
        "image_url": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Bedroom",
        "style": "Contemporary",
        "is_active": True
    },

    # WARDROBES
    {
        "name": "Bergen 3-Door Solid Pine Wardrobe",
        "category": "wardrobes",
        "description": "Spacious three-door wardrobe with full-width hanging rail, four adjustable shelves, and two deep smooth-glide lower drawers.",
        "price": 31999,
        "material": "Solid Scandinavian Pine",
        "colour": "Smoked White Wash",
        "dimensions": "W 150cm x D 60cm x H 200cm",
        "stock": 4,
        "image_url": "https://images.unsplash.com/photo-1558997519-83ea9252edf8?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Kyoto Sliding Door Slatted Wardrobe",
        "category": "wardrobes",
        "description": "Japanese aesthetic sliding slatted doors for smooth operation in tight spaces. Modular internal shelving layout.",
        "price": 35499,
        "material": "Bamboo & Engineered Wood",
        "colour": "Caramel Bamboo",
        "dimensions": "W 160cm x D 62cm x H 205cm",
        "stock": 3,
        "image_url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Minimalist",
        "is_active": True
    },
    {
        "name": "Colonial Solid Teak Armoire",
        "category": "wardrobes",
        "description": "Stately 2-door armoire handcrafted from seasoned reclaimed teak with vintage brass lock and keys.",
        "price": 39999,
        "material": "Reclaimed Solid Teak & Brass",
        "colour": "Rich Dark Teak",
        "dimensions": "W 120cm x D 58cm x H 195cm",
        "stock": 3,
        "image_url": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Traditional",
        "is_active": True
    },

    # STORAGE
    {
        "name": "Malmo 6-Drawer Low Credenza",
        "category": "storage",
        "description": "Low profile side credenza with soft-close Blum drawer runners and recessed handle pulls. Perfect for TV media or dining buffet.",
        "price": 17499,
        "material": "Walnut Veneer & Solid Wood Legs",
        "colour": "Warm Walnut",
        "dimensions": "W 160cm x D 45cm x H 70cm",
        "stock": 7,
        "image_url": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Dining Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Linear Modular Bookshelf 5-Tier",
        "category": "storage",
        "description": "Open-air architecture bookcase featuring five tiered solid oak shelves held by architectural black metal uprights.",
        "price": 14299,
        "material": "Solid Oak & Powder Coated Iron",
        "colour": "Golden Oak & Matte Black",
        "dimensions": "W 100cm x D 35cm x H 180cm",
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1594653245465-985653b1b630?auto=format&fit=crop&w=800&q=80",
        "room_types": "Study Room,Living Room",
        "style": "Minimalist",
        "is_active": True
    },
    {
        "name": "Fjord Solid Pine Nightstand Pair",
        "category": "storage",
        "description": "Set of two compact bedside tables each with a pull-out drawer and an open lower cubby for books and magazines.",
        "price": 7499,
        "material": "Solid Pine Wood",
        "colour": "Natural Matte Lacquer",
        "dimensions": "W 45cm x D 40cm x H 55cm (each)",
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1532372320572-cda25653a26d?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom",
        "style": "Minimalist",
        "is_active": True
    },

    # LIGHTING
    {
        "name": "Apollo Architectural Arc Floor Lamp",
        "category": "lighting",
        "description": "Sweeping cantilever brass floor lamp with heavy white Carrara marble stabilizing base and adjustable domed shade.",
        "price": 8999,
        "material": "Brushed Brass & Carrara Marble",
        "colour": "Warm Gold / White",
        "dimensions": "Span 140cm x H 205cm",
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Study Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Nara Ceramic Bedside Pendant Lamp",
        "category": "lighting",
        "description": "Hand-thrown fluted ceramic pendant with warm ambient glow and brass ceiling canopy hardware.",
        "price": 3899,
        "material": "Terracotta Ceramic & Brass",
        "colour": "Warm Bisque",
        "dimensions": "Dia 24cm x H 18cm, Cord 150cm",
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom,Dining Room",
        "style": "Minimalist",
        "is_active": True
    },
    {
        "name": "Oxford Brass Articulated Task Lamp",
        "category": "lighting",
        "description": "Counterweighted adjustable brass desk lamp with heavy cast base and focused reading spotlight reflector.",
        "price": 4599,
        "material": "Solid Antique Brass",
        "colour": "Antique Brass",
        "dimensions": "H 50cm x Reach 45cm",
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1534349762230-e0cadf78f5da?auto=format&fit=crop&w=800&q=80",
        "room_types": "Study Room,Bedroom",
        "style": "Traditional",
        "is_active": True
    },

    # DECOR
    {
        "name": "Atlas Hand-Knotted Wool Area Rug",
        "category": "decor",
        "description": "Geometric Moroccan Berber-inspired high pile rug hand-knotted from 100% undyed New Zealand wool.",
        "price": 11999,
        "material": "100% Pure Wool",
        "colour": "Ivory with Charcoal Lattice",
        "dimensions": "200cm x 300cm",
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Bedroom",
        "style": "Contemporary",
        "is_active": True
    },
    {
        "name": "Aura Arch Full-Length Mirror",
        "category": "decor",
        "description": "Gracefully arched floor-standing or wall-mounted vanity mirror with ultra-slim anodized matte bronze frame.",
        "price": 7999,
        "material": "Shatter-proof Glass & Aluminium",
        "colour": "Muted Bronze",
        "dimensions": "W 65cm x H 175cm",
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80",
        "room_types": "Bedroom,Living Room",
        "style": "Modern",
        "is_active": True
    },
    {
        "name": "Kyoto Stoneware Vases (Trio)",
        "category": "decor",
        "description": "Collection of three distinct wabi-sabi matte textured ceramic vessels designed for botanical branches or dry floral displays.",
        "price": 2899,
        "material": "Artisanal Glazed Stoneware",
        "colour": "Earthy Sandstone",
        "dimensions": "Heights: 16cm, 22cm, 28cm",
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?auto=format&fit=crop&w=800&q=80",
        "room_types": "Living Room,Dining Room,Study Room",
        "style": "Minimalist",
        "is_active": True
    }
]


def seed_database(app):
    """Initializes and seeds initial database with admin and sample data."""
    with app.app_context():
        db.create_all()

        # Seed Admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@furnispace.local',
                role='admin',
                full_name='FurniSpace Administrator',
                phone='+91 98765 43210',
                address='FurniSpace HQ, Design District'
            )
            admin.set_password('AdminPassword123!')
            db.session.add(admin)

        # Seed Demo Customers
        demo_customer = User.query.filter_by(username='john_doe').first()
        if not demo_customer:
            demo_customer = User(
                username='john_doe',
                email='john@example.com',
                role='customer',
                full_name='John Doe',
                phone='+91 91234 56789',
                address='42 Blossom Avenue, Bangalore, Karnataka'
            )
            demo_customer.set_password('CustomerPass123!')
            db.session.add(demo_customer)

        demo_customer2 = User.query.filter_by(username='sarah_m').first()
        if not demo_customer2:
            demo_customer2 = User(
                username='sarah_m',
                email='sarah@example.com',
                role='customer',
                full_name='Sarah Miller',
                phone='+91 99887 76655',
                address='108 Lake View Estate, Pune, Maharashtra'
            )
            demo_customer2.set_password('CustomerPass123!')
            db.session.add(demo_customer2)

        db.session.commit()

        # Seed Products if table is empty
        if Product.query.count() == 0:
            for item in SAMPLE_PRODUCTS:
                product = Product(**item)
                db.session.add(product)
            db.session.commit()

        # Seed Resale Listings if table is empty
        if ResaleListing.query.count() == 0:
            # 1 Approved
            listing1 = ResaleListing(
                user_id=demo_customer.id,
                title="Mid-Century Wooden Coffee Table",
                category="tables",
                description="Selling our beloved solid teak mid-century coffee table. Relocating abroad. Excellent condition with minimal gentle patina.",
                asking_price=4200,
                condition="Gently Used",
                location="Indiranagar, Bangalore",
                contact_info="john.resale@example.com | 9123456789",
                image_url="https://images.unsplash.com/photo-1533090161767-e6ffed986c88?auto=format&fit=crop&w=800&q=80",
                status="Approved",
                admin_notes="Verified images and reasonable price."
            )
            # 1 Pending
            listing2 = ResaleListing(
                user_id=demo_customer2.id,
                title="Grey Ergonomic Mesh Study Chair",
                category="chairs",
                description="Bought 6 months ago for work from home. Adjustable armrests, lumbar support pad, breathable mesh back. Moving to office.",
                asking_price=3500,
                condition="Like New",
                location="Koregaon Park, Pune",
                contact_info="sarah.seller@example.com | 9988776655",
                image_url="https://images.unsplash.com/photo-1580481077197-0335e23970b8?auto=format&fit=crop&w=800&q=80",
                status="Pending"
            )
            # 1 Rejected
            listing3 = ResaleListing(
                user_id=demo_customer.id,
                title="Damaged Fabric Bean Bag",
                category="chairs",
                description="Old bean bag, small tear on side seam, filler needed.",
                asking_price=800,
                condition="Fair",
                location="Bangalore",
                contact_info="john@example.com",
                image_url="https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80",
                status="Rejected",
                admin_notes="Item condition does not meet quality standards for resale."
            )
            db.session.add_all([listing1, listing2, listing3])
            db.session.commit()

        print("Database initialized and seeded successfully!")


if __name__ == '__main__':
    from flask import Flask
    from config import Config

    test_app = Flask(__name__)
    test_app.config.from_object(Config)
    db.init_app(test_app)
    seed_database(test_app)
