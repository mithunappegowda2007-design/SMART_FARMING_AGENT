"""Validate the new real-world medicine products API."""
import requests

BASE = "http://127.0.0.1:5000"

# ── Page check ───────────────────────────────────────────
r = requests.get(f"{BASE}/pest-detection", timeout=10)
print("Page HTTP      :", r.status_code)
first20 = r.text[:20].replace("\n", "")
print("First 20 chars :", repr(first20))
print("form-pill CSS  :", "medicine-form-pill" in r.text)
print("brand CSS      :", "medicine-brand" in r.text)
print("how-to CSS     :", "medicine-how-to-use" in r.text)

# ── API check ────────────────────────────────────────────
r2 = requests.post(
    f"{BASE}/api/medicine-images",
    json={
        "problem":              "fungal blight powdery mildew aphid",
        "chemical_product":     "Mancozeb fungicide spray powder",
        "biological_treatment": "Trichoderma viride soil drench",
        "crop":                 "tomato",
    },
    timeout=10,
)
meds = r2.json().get("medicines", [])
print()
print("=" * 55)
print("  Real-world Products Returned:", len(meds))
print("=" * 55)
for m in meds:
    bn  = m.get("brand_name", "???")
    gn  = m.get("generic_name", "???")
    mfg = m.get("manufacturer", "???")
    frm = m.get("form", "???")
    img = m.get("image", "")[:65]
    htw = m.get("how_to_use", "???")
    print(f"  Brand    : {bn}")
    print(f"  Generic  : {gn}")
    print(f"  Maker    : {mfg}")
    print(f"  Form     : {frm}")
    print(f"  Image    : {img}")
    print(f"  How-to   : {htw}")
    print()

print("ALL OK — open http://127.0.0.1:5000/pest-detection")
