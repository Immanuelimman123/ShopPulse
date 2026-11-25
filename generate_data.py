from pathlib import Path
import random
import numpy as np
import pandas as pd

# Re-run this file whenever you want to regenerate the synthetic data.
# The random seed keeps the output reproducible.
rng = np.random.default_rng(42)
random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

categories = {
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Bluetooth Speaker", "Power Bank", "Keyboard", "Mouse"],
    "Fashion": ["T-Shirt", "Jeans", "Sneakers", "Backpack", "Jacket", "Dress"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Storage Set", "Bedsheet", "Water Bottle", "Mixer"],
    "Beauty": ["Face Wash", "Moisturizer", "Shampoo", "Sunscreen", "Perfume", "Hair Dryer"],
    "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Gym Bag", "Cricket Bat", "Football"]
}
price_ranges = {
    "Electronics": (500, 18000), "Fashion": (300, 6000),
    "Home & Kitchen": (250, 12000), "Beauty": (150, 3500), "Sports": (250, 9000)
}

products = []
for i in range(1, 101):
    category = list(categories)[(i - 1) % len(categories)]
    low, high = price_ranges[category]
    price = round(float(rng.uniform(low, high)), 2)
    cost = round(price * float(rng.uniform(0.48, 0.76)), 2)
    products.append({
        "Product_ID": f"P{i:04d}",
        "Product_Name": f"{random.choice(categories[category])} {((i-1)//5)+1}",
        "Category": category, "Unit_Price": price, "Unit_Cost": cost,
        "Brand": random.choice(["Nova", "UrbanLeaf", "Aster", "PixelPro", "DailyNest", "FitCore"]),
        "Supplier": random.choice(["Supplier A", "Supplier B", "Supplier C", "Supplier D"])
    })
products_df = pd.DataFrame(products)

cities_regions = [
    ("Chennai", "South"), ("Bengaluru", "South"), ("Hyderabad", "South"), ("Kochi", "South"),
    ("Mumbai", "West"), ("Pune", "West"), ("Ahmedabad", "West"), ("Jaipur", "North"),
    ("Delhi", "North"), ("Lucknow", "North"), ("Kolkata", "East"), ("Bhubaneswar", "East")
]
first_names = ["Aarav", "Diya", "Ishaan", "Ananya", "Vivaan", "Meera", "Arjun", "Sana", "Kavin", "Nila",
               "Rohan", "Aadhya", "Kabir", "Ira", "Dev", "Maya", "Advik", "Tara", "Neil", "Kiara"]
last_names = ["Sharma", "Patel", "Kumar", "Reddy", "Iyer", "Mehta", "Nair", "Das", "Rao", "Singh"]

customers = []
for i in range(1, 2501):
    city, region = cities_regions[int(rng.integers(0, len(cities_regions)))]
    customers.append({
        "Customer_ID": f"C{i:05d}",
        "Customer_Name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Age": int(rng.integers(18, 71)),
        "Gender": random.choice(["Female", "Male", "Prefer not to say"]),
        "City": city, "Region": region,
        "Signup_Date": (pd.Timestamp("2023-01-01") + pd.Timedelta(days=int(rng.integers(0, 900)))).date().isoformat(),
        "Customer_Segment": random.choice(["New", "Regular", "Loyal", "VIP"])
    })
customers_df = pd.DataFrame(customers)

product_lookup = products_df.set_index("Product_ID").to_dict("index")
customer_lookup = pd.DataFrame(customers).set_index("Customer_ID").to_dict("index")
product_ids = products_df["Product_ID"].to_numpy()
customer_ids = pd.DataFrame(customers)["Customer_ID"].to_numpy()
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")

orders = []
for i in range(1, 10001):
    product_id = str(rng.choice(product_ids))
    customer_id = str(rng.choice(customer_ids))
    product = product_lookup[product_id]
    customer = customer_lookup[customer_id]
    order_date = pd.Timestamp(rng.choice(dates))
    quantity = int(rng.choice([1, 1, 1, 2, 2, 3, 4]))
    discount_pct = float(rng.choice([0, 0, 0.05, 0.10, 0.15, 0.20]))
    gross = product["Unit_Price"] * quantity
    discount = round(gross * discount_pct, 2)
    revenue = round(gross - discount, 2)
    cost = round(product["Unit_Cost"] * quantity, 2)
    status = str(rng.choice(
        ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"],
        p=[0.76, 0.10, 0.07, 0.04, 0.03]
    ))
    orders.append({
        "Order_ID": f"ORD{i:06d}", "Order_Date": order_date.date().isoformat(),
        "Customer_ID": customer_id, "Product_ID": product_id, "Quantity": quantity,
        "Unit_Price": product["Unit_Price"], "Discount_Pct": discount_pct,
        "Discount_Amount": discount, "Revenue": revenue, "Cost": cost,
        "Profit": round(revenue - cost, 2),
        "Payment_Method": random.choice(["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]),
        "Order_Status": status, "City": customer["City"], "Region": customer["Region"],
        "Category": product["Category"], "Product_Name": product["Product_Name"]
    })

orders_df = pd.DataFrame(orders)
inventory = []
for _, product in products_df.iterrows():
    stock = int(rng.integers(0, 500))
    reorder_level = int(rng.integers(30, 100))
    inventory.append({
        "Product_ID": product["Product_ID"], "Product_Name": product["Product_Name"],
        "Category": product["Category"], "Current_Stock": stock,
        "Reorder_Level": reorder_level,
        "Stock_Status": "Low Stock" if stock <= reorder_level else "Healthy",
        "Unit_Cost": product["Unit_Cost"],
        "Stock_Value": round(stock * product["Unit_Cost"], 2)
    })
inventory_df = pd.DataFrame(inventory)

orders_df.to_csv(DATA_DIR / "orders.csv", index=False)
customers_df.to_csv(DATA_DIR / "customers.csv", index=False)
products_df.to_csv(DATA_DIR / "products.csv", index=False)
inventory_df.to_csv(DATA_DIR / "inventory.csv", index=False)

print("Synthetic datasets generated successfully!")
print(f"Orders: {len(orders_df):,}")
print(f"Customers: {len(customers_df):,}")
print(f"Products: {len(products_df):,}")
print(f"Inventory records: {len(inventory_df):,}")
