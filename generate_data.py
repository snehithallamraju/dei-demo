"""Generate the demo dataset: orders for a fictional Agra food-delivery business.

Planted on purpose (these ARE the demo):
  - Mama's Kitchen is really the #1 restaurant, but its name is spelled 4 ways,
    so on the raw data Agra Tandoor House looks like #1  (MDM step)
  - Mixed date formats, prices stored as text with the rupee sign, blank cells,
    "min" suffixes, messy area casing, duplicate rows      (Data Engineer step)
  - Deliveries in Sikandra and Shahganj get slower every month, and customers
    who get a late delivery (>45 min) come back far less     (Analyst step)

Run:  python generate_data.py      -> data/orders_raw.csv
Seeded, so the output is identical every time.
"""
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

START, END = date(2026, 1, 1), date(2026, 6, 30)
AREAS = ["Tajganj", "Sikandra", "Kamla Nagar", "Dayalbagh",
         "Shahganj", "Civil Lines", "Sanjay Place", "Balkeshwar"]
SLOW_AREAS = {"Sikandra", "Shahganj"}

# (canonical name, share of orders, avg order value in INR)
RESTAURANTS = [
    ("Mama's Kitchen", 0.24, 340),
    ("Agra Tandoor House", 0.15, 360),
    ("Taj Biryani Co", 0.13, 320),
    ("Petha Point Cafe", 0.10, 180),
    ("Kamla Nagar Chaat Corner", 0.10, 150),
    ("Crust & Co Pizza", 0.11, 420),
    ("Southern Spice", 0.09, 260),
    ("Green Bowl Salads", 0.08, 290),
]
MAMA_VARIANTS = [("Mama's Kitchen", 0.34), ("MAMAS KITCHEN", 0.26),
                 ("Mama's Kitchen - Agra", 0.24), ("mamas kitchen ", 0.16)]


def pick(weighted):
    r, acc = random.random(), 0.0
    for item, w in weighted:
        acc += w
        if r <= acc:
            return item
    return weighted[-1][0]


def delivery_minutes(area, d):
    months_in = (d.year - 2026) * 12 + d.month - 1  # 0 for Jan
    base = random.gauss(31, 7)
    if area in SLOW_AREAS:
        base += 2 + months_in * 6  # gets worse every month
    return max(12, round(base))


def messy_date(d):
    fmt = random.random()
    if fmt < 0.6:
        return d.strftime("%Y-%m-%d")
    if fmt < 0.85:
        return d.strftime("%d/%m/%Y")
    return d.strftime("%b %d %Y")


def messy_amount(a):
    r = random.random()
    if r < 0.02:
        return ""
    if r < 0.45:
        return f"₹{a}"
    if r < 0.7:
        return f"{a}.00"
    return str(a)


def messy_minutes(m):
    r = random.random()
    if r < 0.015:
        return ""
    if r < 0.2:
        return f"{m} min"
    return str(m)


def messy_area(a):
    r = random.random()
    if r < 0.12:
        return a.upper()
    if r < 0.22:
        return a.lower() + " "
    return a


rows = []
customer_count = 1100
for c in range(1, customer_count + 1):
    cust = f"C{c:04d}"
    area = random.choice(sorted(SLOW_AREAS)) if random.random() < 0.34 else random.choice(AREAS)
    d = START + timedelta(days=random.randint(0, 150))
    while d <= END:
        name, _, avg = None, None, None
        canon = pick([(r[0], r[1]) for r in RESTAURANTS])
        avg = next(r[2] for r in RESTAURANTS if r[0] == canon)
        name = pick(MAMA_VARIANTS) if canon == "Mama's Kitchen" else canon
        amount = max(80, int(random.gauss(avg, avg * 0.25)))
        mins = delivery_minutes(area, d)
        rows.append([d, cust, area, name, amount, mins])
        late = mins > 45
        if random.random() > (0.32 if late else 0.80):
            break  # customer does not come back
        d += timedelta(days=random.randint(4, 24))

rows.sort(key=lambda r: r[0])
out = []
for i, (d, cust, area, name, amount, mins) in enumerate(rows, start=1):
    oid = "" if random.random() < 0.008 else f"ORD-{i:05d}"
    out.append([oid, messy_date(d), cust, messy_area(area), name,
                messy_amount(amount), messy_minutes(mins)])

# duplicate ~2% of rows (the same order loaded twice)
for r in random.sample(out, k=len(out) // 50):
    out.insert(random.randint(0, len(out)), list(r))

os.makedirs("data", exist_ok=True)
with open("data/orders_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Order ID", "Order Date", "Customer", "Area",
                "Restaurant Name", "Amount", "Delivery Time"])
    w.writerows(out)

print(f"Wrote {len(out)} rows to data/orders_raw.csv")
