"""Quick endpoint test — run after server is up."""
import requests
import json

BASE = "http://127.0.0.1:5000"

def sep(title):
    print("\n" + "="*55)
    print(f"  {title}")
    print("="*55)

# ── 1. Pest Detection ──────────────────────────────────────
sep("TEST 1 — /api/pest-detection")
r = requests.post(
    f"{BASE}/api/pest-detection",
    data={
        "crop": "tomato",
        "symptoms": "white powdery coating on leaves and stems",
        "location": "Karnataka",
    },
    timeout=15,
)
print("HTTP:", r.status_code)
d = r.json()
print("Success:", d.get("success"))
pd = d.get("data", {})
print("Problem :", pd.get("identified_problem"))
print("Severity:", pd.get("severity"))
print("Confidence:", pd.get("confidence"))
chem = pd.get("chemical_treatment", {})
print("Chemical:", chem.get("product"))
print("Bio    :", str(pd.get("biological_treatment", ""))[:80])

# ── 2. Medicine Images ─────────────────────────────────────
sep("TEST 2 — /api/medicine-images")
r2 = requests.post(
    f"{BASE}/api/medicine-images",
    json={
        "problem": pd.get("identified_problem", "fungal blight aphid"),
        "chemical_product": chem.get("product", "Mancozeb"),
        "biological_treatment": pd.get("biological_treatment", "Trichoderma"),
        "crop": "tomato",
    },
    timeout=15,
)
print("HTTP:", r2.status_code)
d2 = r2.json()
print("Success:", d2.get("success"))
meds = d2.get("medicines", [])
print(f"Medicines returned: {len(meds)}")
for m in meds:
    cat = m.get("category", "")
    name = m.get("name", "")
    img = m.get("image", "")
    emoji = m.get("emoji", "")
    desc = m.get("description", "")[:60]
    print(f"  {emoji}  [{cat}]  {name}")
    print(f"      desc : {desc}")
    print(f"      image: {img}")

# ── 3. Full combined flow ──────────────────────────────────
sep("TEST 3 — combined (aphid on rice)")
r3 = requests.post(
    f"{BASE}/api/pest-detection",
    data={
        "crop": "rice",
        "symptoms": "small insects under leaves, yellow sticky residue, curling leaves",
        "location": "Punjab",
    },
    timeout=15,
)
pd3 = r3.json().get("data", {})
chem3 = pd3.get("chemical_treatment", {})

r4 = requests.post(
    f"{BASE}/api/medicine-images",
    json={
        "problem": pd3.get("identified_problem", ""),
        "chemical_product": chem3.get("product", ""),
        "biological_treatment": pd3.get("biological_treatment", ""),
        "crop": "rice",
    },
    timeout=15,
)
meds4 = r4.json().get("medicines", [])
print(f"Pest detected : {pd3.get('identified_problem')}")
print(f"Medicines shown: {len(meds4)}")
for m in meds4:
    print(f"  {m.get('emoji')}  {m.get('name')}  ({m.get('category')})")

sep("ALL TESTS PASSED")
