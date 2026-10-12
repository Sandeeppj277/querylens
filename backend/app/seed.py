"""
Seed the database with realistic e-commerce data.

Run:  python -m app.seed
"""

import random
from datetime import datetime, timedelta
from app.database import engine, SessionLocal, Base
from app.models import Category, Product, Customer, Order, OrderItem, Review


def seed():
    """Drop all tables, recreate, and populate with sample data."""
    print("[*] Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    print("[*] Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── 1. Categories ────────────────────────────────────
        categories_data = [
            ("Electronics", "Smartphones, laptops, tablets, and accessories"),
            ("Clothing", "Men's and women's apparel, shoes, and accessories"),
            ("Books", "Fiction, non-fiction, textbooks, and e-books"),
            ("Home & Kitchen", "Furniture, appliances, and home decor"),
            ("Sports & Outdoors", "Fitness equipment, camping, and sportswear"),
            ("Beauty & Health", "Skincare, makeup, vitamins, and wellness"),
        ]
        categories = []
        for name, desc in categories_data:
            cat = Category(name=name, description=desc)
            db.add(cat)
            categories.append(cat)
        db.flush()
        print(f"   [OK] {len(categories)} categories")

        # ── 2. Products ──────────────────────────────────────
        products_data = [
            # Electronics
            ("iPhone 15 Pro", 1, 999.99, 45),
            ("Samsung Galaxy S24", 1, 849.99, 60),
            ("MacBook Air M3", 1, 1299.00, 30),
            ("Sony WH-1000XM5 Headphones", 1, 349.99, 80),
            ("iPad Air", 1, 599.99, 55),
            ("Dell XPS 15", 1, 1449.00, 25),
            ("AirPods Pro 2", 1, 249.99, 120),
            ("Nintendo Switch OLED", 1, 349.99, 40),
            # Clothing
            ("Levi's 501 Jeans", 2, 69.99, 200),
            ("Nike Air Max 90", 2, 129.99, 150),
            ("Adidas Ultraboost", 2, 189.99, 90),
            ("North Face Puffer Jacket", 2, 299.00, 45),
            ("Ray-Ban Aviator Sunglasses", 2, 163.00, 70),
            ("Uniqlo Cashmere Sweater", 2, 99.90, 110),
            # Books
            ("Atomic Habits", 3, 16.99, 300),
            ("The Great Gatsby", 3, 9.99, 250),
            ("Python Crash Course", 3, 39.99, 180),
            ("Sapiens", 3, 18.99, 200),
            ("Dune", 3, 14.99, 160),
            ("Clean Code", 3, 44.99, 140),
            # Home & Kitchen
            ("Instant Pot Duo 7-in-1", 4, 89.99, 95),
            ("Dyson V15 Vacuum", 4, 749.99, 35),
            ("KitchenAid Stand Mixer", 4, 379.99, 50),
            ("Nespresso Vertuo Plus", 4, 159.00, 65),
            ("iRobot Roomba j7+", 4, 599.99, 40),
            # Sports & Outdoors
            ("Peloton Bike", 5, 1445.00, 20),
            ("Yeti Rambler 30oz", 5, 38.00, 300),
            ("Coleman Sundome Tent", 5, 79.99, 85),
            ("Fitbit Charge 6", 5, 159.95, 100),
            ("Hydro Flask 32oz", 5, 44.95, 250),
            # Beauty & Health
            ("CeraVe Moisturizing Cream", 6, 18.99, 400),
            ("Dyson Airwrap", 6, 599.99, 30),
            ("Vitamin D3 5000IU (365 ct)", 6, 14.99, 500),
            ("Olaplex No.3 Hair Perfector", 6, 30.00, 180),
            ("Oral-B iO Series 9", 6, 299.99, 55),
        ]

        products = []
        base_date = datetime(2025, 1, 1)
        for name, cat_idx, price, stock in products_data:
            prod = Product(
                name=name,
                category_id=categories[cat_idx - 1].id,
                price=price,
                stock_quantity=stock,
                created_at=base_date + timedelta(days=random.randint(0, 180)),
            )
            db.add(prod)
            products.append(prod)
        db.flush()
        print(f"   [OK] {len(products)} products")

        # ── 3. Customers ─────────────────────────────────────
        customers_data = [
            ("Aarav", "Sharma", "aarav.sharma@email.com", "Mumbai", "India"),
            ("Priya", "Patel", "priya.patel@email.com", "Delhi", "India"),
            ("Rahul", "Gupta", "rahul.gupta@email.com", "Bangalore", "India"),
            ("Sneha", "Reddy", "sneha.reddy@email.com", "Hyderabad", "India"),
            ("Vikram", "Singh", "vikram.singh@email.com", "Chennai", "India"),
            ("Ananya", "Nair", "ananya.nair@email.com", "Kochi", "India"),
            ("John", "Smith", "john.smith@email.com", "New York", "USA"),
            ("Emma", "Wilson", "emma.wilson@email.com", "London", "UK"),
            ("Li", "Wei", "li.wei@email.com", "Shanghai", "China"),
            ("Yuki", "Tanaka", "yuki.tanaka@email.com", "Tokyo", "Japan"),
            ("Carlos", "Garcia", "carlos.garcia@email.com", "Madrid", "Spain"),
            ("Sophie", "Dubois", "sophie.dubois@email.com", "Paris", "France"),
            ("Arjun", "Kumar", "arjun.kumar@email.com", "Pune", "India"),
            ("Meera", "Joshi", "meera.joshi@email.com", "Ahmedabad", "India"),
            ("Rohan", "Verma", "rohan.verma@email.com", "Jaipur", "India"),
            ("Kavita", "Desai", "kavita.desai@email.com", "Surat", "India"),
            ("Amit", "Choudhury", "amit.choudhury@email.com", "Kolkata", "India"),
            ("Divya", "Menon", "divya.menon@email.com", "Trivandrum", "India"),
            ("Sanjay", "Rao", "sanjay.rao@email.com", "Mysore", "India"),
            ("Neha", "Kapoor", "neha.kapoor@email.com", "Chandigarh", "India"),
        ]

        customers = []
        for fname, lname, email, city, country in customers_data:
            cust = Customer(
                first_name=fname,
                last_name=lname,
                email=email,
                city=city,
                country=country,
                joined_at=base_date + timedelta(days=random.randint(0, 365)),
            )
            db.add(cust)
            customers.append(cust)
        db.flush()
        print(f"   [OK] {len(customers)} customers")

        # ── 4. Orders & Order Items ──────────────────────────
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        status_weights = [0.05, 0.10, 0.15, 0.60, 0.10]  # most are delivered

        orders = []
        all_items = []

        # Generate ~120 orders spread over the past 18 months
        for _ in range(120):
            customer = random.choice(customers)
            order_date = datetime(2025, 4, 1) + timedelta(
                days=random.randint(0, 550),
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59),
            )
            status = random.choices(statuses, weights=status_weights, k=1)[0]

            order = Order(
                customer_id=customer.id,
                order_date=order_date,
                status=status,
                total_amount=0,
            )
            db.add(order)
            db.flush()

            # Each order has 1-5 items
            num_items = random.randint(1, 5)
            chosen_products = random.sample(products, min(num_items, len(products)))
            order_total = 0.0

            for prod in chosen_products:
                qty = random.randint(1, 4)
                item = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=prod.price,
                )
                db.add(item)
                all_items.append(item)
                order_total += prod.price * qty

            order.total_amount = round(order_total, 2)
            orders.append(order)

        db.flush()
        print(f"   [OK] {len(orders)} orders with {len(all_items)} line items")

        # ── 5. Reviews ───────────────────────────────────────
        reviews = []
        review_comments = [
            "Absolutely love it! Worth every penny.",
            "Good product, fast delivery.",
            "Decent quality for the price.",
            "Not what I expected. Returning it.",
            "Amazing quality! Would buy again.",
            "Average product, nothing special.",
            "Best purchase I've made this year!",
            "Broke after two weeks. Disappointed.",
            "Great value for money.",
            "Five stars! Highly recommended.",
            "Okay product. Packaging was damaged.",
            "Exceeds expectations in every way.",
            "Terrible customer support experience.",
            "Perfect gift for my family.",
            "Solid build quality. Very satisfied.",
        ]

        for _ in range(80):
            prod = random.choice(products)
            cust = random.choice(customers)
            rating = random.choices(
                [1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.15, 0.35, 0.35], k=1
            )[0]
            review = Review(
                product_id=prod.id,
                customer_id=cust.id,
                rating=rating,
                comment=random.choice(review_comments),
                created_at=datetime(2025, 6, 1) + timedelta(days=random.randint(0, 480)),
            )
            db.add(review)
            reviews.append(review)
        db.flush()
        print(f"   [OK] {len(reviews)} reviews")

        db.commit()
        print("\n[SUCCESS] Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
