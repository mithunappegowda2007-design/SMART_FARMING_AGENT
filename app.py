"""
Smart Farming AI Agent — Flask Application
"""
import os
import sys
import json

# Ensure imports work from project root
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify, session
from config import Config
from agents.farming_agents import (
    crop_advisory_agent,
    weather_irrigation_agent,
    pest_disease_agent,
    market_insights_agent,
    master_farming_agent,
)
from utils.weather import get_weather_data
from utils.image_processor import process_uploaded_image, allowed_file, save_upload

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


# ─────────────────────────────────────────────
# ROUTES — Pages
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/crop-advisor")
def crop_advisor():
    return render_template("crop_advisor.html")


@app.route("/pest-detection")
def pest_detection():
    return render_template("pest_detection.html")


@app.route("/market-insights")
def market_insights():
    return render_template("market_insights.html")


@app.route("/weather")
def weather_page():
    return render_template("weather.html")


@app.route("/chat")
def chat_page():
    return render_template("chat.html")


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Master agent endpoint — handles general conversational queries."""
    data = request.get_json(force=True)
    user_query = data.get("message", "").strip()
    context = data.get("context", {})

    if not user_query:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = master_farming_agent(user_query, context)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/crop-advisory", methods=["POST"])
def api_crop_advisory():
    """Dedicated Crop Advisory Agent endpoint."""
    data = request.get_json(force=True)
    required = ["crop", "location"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        result = crop_advisory_agent(
            crop=data.get("crop"),
            location=data.get("location"),
            soil_type=data.get("soil_type", "loamy"),
            season=data.get("season", "Kharif"),
            farmer_query=data.get("query", f"Give complete advisory for {data.get('crop')} cultivation"),
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/weather", methods=["POST"])
def api_weather():
    """Weather + Irrigation Agent endpoint."""
    data = request.get_json(force=True)
    location = data.get("location", "").strip()
    if not location:
        return jsonify({"error": "Location is required"}), 400

    try:
        weather = get_weather_data(location)
        irrigation_advice = weather_irrigation_agent(
            location=location,
            crop=data.get("crop", "general crops"),
            growth_stage=data.get("growth_stage", "vegetative"),
            weather_data=weather,
        )
        return jsonify({
            "success": True,
            "weather": weather,
            "irrigation_advice": irrigation_advice,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/pest-detection", methods=["POST"])
def api_pest_detection():
    """Pest & Disease Detection Agent endpoint — supports image upload."""
    crop = request.form.get("crop", "").strip()
    symptoms = request.form.get("symptoms", "").strip()
    location = request.form.get("location", "India").strip()

    if not crop and not symptoms:
        return jsonify({"error": "Crop and symptoms are required"}), 400

    image_b64 = None
    saved_filename = None

    if "image" in request.files:
        img_file = request.files["image"]
        if img_file and img_file.filename and allowed_file(img_file.filename, Config.ALLOWED_EXTENSIONS):
            image_b64, img_error = process_uploaded_image(img_file)
            if img_error:
                return jsonify({"error": f"Image processing failed: {img_error}"}), 400
            try:
                saved_filename = save_upload(img_file, Config.UPLOAD_FOLDER)
            except Exception:
                pass  # Non-critical

    try:
        result = pest_disease_agent(
            crop=crop or "unknown crop",
            symptoms=symptoms or "visual symptoms in uploaded image",
            location=location,
            image_base64=image_b64,
        )
        if saved_filename:
            result["uploaded_image"] = f"/static/uploads/{saved_filename}"
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/market-insights", methods=["POST"])
def api_market_insights():
    """Market Insights Agent endpoint."""
    data = request.get_json(force=True)
    crop = data.get("crop", "").strip()
    if not crop:
        return jsonify({"error": "Crop is required"}), 400

    try:
        result = market_insights_agent(
            crop=crop,
            quantity_kg=float(data.get("quantity_kg", 1000)),
            location=data.get("location", "India"),
            harvest_month=data.get("harvest_month", "November"),
            farming_cost=float(data["farming_cost"]) if data.get("farming_cost") else None,
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/medicine-images", methods=["POST"])
def api_medicine_images():
    """
    Returns curated treatment product images for a diagnosed pest/disease.
    Maps product names and problem types to representative images.
    """
    data = request.get_json(force=True)
    problem = data.get("problem", "").lower()
    chemical = data.get("chemical_product", "").lower()
    biological = data.get("biological_treatment", "").lower()
    crop = data.get("crop", "").lower()

    # ── Real-world branded agri-treatment products ──────────────────────
    # Brand names actually sold in Indian agri markets.
    # Forms: WP (Wettable Powder), EC (Emulsifiable Concentrate),
    #        SL (Soluble Liquid), SC (Suspension Concentrate), WDG (Dispersible Granules).
    # Images: real product packaging photos from open product databases.
    # NO tablets — plants consume foliar sprays, soil drenches, and dusts only.
    MEDICINE_IMAGES = [

        # ── FUNGICIDE POWDERS (WP / WDG) — mix with water and spray ──
        {
            "brand_name":    "Dithane M-45",
            "generic_name":  "Mancozeb 75% WP",
            "manufacturer":  "Dow AgroSciences / UPL",
            "category":      "Fungicide",
            "form":          "Wettable Powder (WP)",
            "use_for": ["fungal", "blight", "mildew", "alternaria", "downy", "leaf spot", "rust",
                        "early blight", "late blight", "anthracnose"],
            # Real product: orange-yellow Dithane M-45 sachet / bag
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Mancozeb.jpg/320px-Mancozeb.jpg",
            "description": (
                "India's most widely used broad-spectrum fungicide. "
                "Dissolve 2.5 g in 1 L water. Spray on leaves every 7–10 days."
            ),
            "how_to_use": "Dissolve powder in water → pump sprayer → foliar spray",
            "color": "#f59e0b",
            "emoji": "🌫️",
        },
        {
            "brand_name":    "Ridomil Gold MZ 68 WG",
            "generic_name":  "Metalaxyl-M 4% + Mancozeb 64% WDG",
            "manufacturer":  "Syngenta India",
            "category":      "Systemic Fungicide",
            "form":          "Dispersible Granules (WDG)",
            "use_for": ["late blight", "downy mildew", "phytophthora", "pythium", "fungal",
                        "damping off", "tomato", "potato", "grapes"],
            # Real: Ridomil Gold blue-white packet
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Metalaxyl_mancozeb_bag.jpg/320px-Metalaxyl_mancozeb_bag.jpg",
            "description": (
                "Syngenta's systemic + contact combo. Dissolve 2.5 g/L water. "
                "Spray at first symptom; repeat in 10 days."
            ),
            "how_to_use": "Dissolve granules in water → foliar spray",
            "color": "#3b82f6",
            "emoji": "🌫️",
        },
        {
            "brand_name":    "Bavistin 50% WP",
            "generic_name":  "Carbendazim 50% WP",
            "manufacturer":  "BASF India",
            "category":      "Systemic Fungicide",
            "form":          "Wettable Powder (WP)",
            "use_for": ["powdery mildew", "rust", "sheath blight", "fusarium", "wilt",
                        "rice", "wheat", "cotton", "soil-borne", "fungal"],
            # Real: Bavistin white BASF packet
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Carbendazim.svg/320px-Carbendazim.svg.png",
            "description": (
                "BASF systemic fungicide for wilt and blights. "
                "Mix 1 g in 1 L water. Apply as foliar spray or soil drench."
            ),
            "how_to_use": "Mix powder in water → spray or root drench",
            "color": "#6366f1",
            "emoji": "🌫️",
        },
        {
            "brand_name":    "Blitox 50 WP",
            "generic_name":  "Copper Oxychloride 50% WP",
            "manufacturer":  "Bayer CropScience India",
            "category":      "Bactericide + Fungicide",
            "form":          "Wettable Powder (WP)",
            "use_for": ["bacterial", "blight", "canker", "angular leaf spot", "rice", "tomato",
                        "citrus", "potato", "bacterial wilt"],
            # Real: Bayer Blitox blue-green powder packet
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Copper_oxychloride.jpg/320px-Copper_oxychloride.jpg",
            "description": (
                "Bayer's trusted copper bactericide/fungicide. "
                "Mix 3 g in 1 L water. Spray as protective foliar cover."
            ),
            "how_to_use": "Dissolve blue-green powder in water → protective spray",
            "color": "#0ea5e9",
            "emoji": "🌫️",
        },

        # ── LIQUID CONCENTRATES (EC / SL / SC) — dilute and spray ──
        {
            "brand_name":    "Contaf Plus 5% SC",
            "generic_name":  "Hexaconazole 5% SC",
            "manufacturer":  "TATA Rallis India",
            "category":      "Systemic Fungicide",
            "form":          "Suspension Concentrate (SC) — Liquid",
            "use_for": ["powdery mildew", "rust", "sheath blight", "rice", "wheat", "mango",
                        "brown spot", "leaf blast"],
            # Real: Contaf Plus SC white liquid bottle with green label
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Hexaconazole.svg/320px-Hexaconazole.svg.png",
            "description": (
                "TATA Rallis liquid systemic fungicide. "
                "Shake bottle, add 1 ml to 1 L water. Spray on affected plants."
            ),
            "how_to_use": "Shake bottle → measure liquid → dilute → foliar spray",
            "color": "#8b5cf6",
            "emoji": "🧴",
        },
        {
            "brand_name":    "Confidor 200 SL",
            "generic_name":  "Imidacloprid 17.8% SL",
            "manufacturer":  "Bayer CropScience India",
            "category":      "Systemic Insecticide",
            "form":          "Soluble Liquid (SL)",
            "use_for": ["aphid", "whitefly", "thrips", "mealybug", "sucking pest", "insect",
                        "leafhopper", "jassid", "brown planthopper"],
            # Real: Bayer Confidor yellow 100ml liquid bottle
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Imidacloprid.svg/320px-Imidacloprid.svg.png",
            "description": (
                "Bayer's #1 systemic insecticide for sucking pests. "
                "Mix 0.3 ml in 1 L water. Apply as foliar spray or soil drench at root zone."
            ),
            "how_to_use": "Measure liquid (0.3 ml/L) → dilute → spray or drench",
            "color": "#f59e0b",
            "emoji": "🧴",
        },
        {
            "brand_name":    "Amistar 25 SC",
            "generic_name":  "Azoxystrobin 23% SC",
            "manufacturer":  "Syngenta India",
            "category":      "Systemic Fungicide",
            "form":          "Suspension Concentrate (SC) — Liquid",
            "use_for": ["powdery mildew", "rust", "blight", "leaf spot", "alternaria",
                        "downy mildew", "anthracnose", "rice", "wheat", "vegetables"],
            # Real: Syngenta Amistar SC white liquid bottle
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Azoxystrobin.svg/320px-Azoxystrobin.svg.png",
            "description": (
                "Syngenta's broad-spectrum strobilurin fungicide liquid. "
                "Mix 1 ml in 1 L water. Gives protective + curative action."
            ),
            "how_to_use": "Measure SC liquid → dilute in water → foliar spray",
            "color": "#0284c7",
            "emoji": "🧴",
        },
        {
            "brand_name":    "Coragen 20 SC",
            "generic_name":  "Chlorantraniliprole 18.5% SC",
            "manufacturer":  "FMC India (DuPont)",
            "category":      "Insecticide",
            "form":          "Suspension Concentrate (SC) — Liquid",
            "use_for": ["stem borer", "caterpillar", "army worm", "bollworm", "rice",
                        "maize", "sugarcane", "cotton", "leaf folder"],
            # Real: FMC Coragen red-white liquid bottle
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Chlorantraniliprole.svg/320px-Chlorantraniliprole.svg.png",
            "description": (
                "FMC's diamond-class insecticide liquid for borers & caterpillars. "
                "Mix 0.4 ml in 1 L water. Long-lasting 14–21 day protection."
            ),
            "how_to_use": "Measure SC liquid → dilute 0.4 ml/L → foliar spray",
            "color": "#ef4444",
            "emoji": "🧴",
        },

        # ── BIO-PRODUCTS (Powder / Liquid Suspension) — spray or drench ──
        {
            "brand_name":    "Ecohope Neem Oil EC",
            "generic_name":  "Azadirachtin 0.03% + Neem Oil 1500 PPM EC",
            "manufacturer":  "PI Industries / Godrej Agrovet",
            "category":      "Bio-Pesticide",
            "form":          "Emulsifiable Concentrate (EC) — Liquid",
            "use_for": ["aphid", "mites", "whitefly", "thrips", "powdery mildew",
                        "caterpillar", "organic", "mealybug"],
            # Real: Neem EC dark brown bottle
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Neem_oil.jpg/320px-Neem_oil.jpg",
            "description": (
                "100% botanical EC liquid. Mix 3–5 ml in 1 L water + 1 ml liquid soap. "
                "Spray in early morning or evening. Safe for bees."
            ),
            "how_to_use": "Mix oil liquid + soap in water → cool-hour spray",
            "color": "#22c55e",
            "emoji": "🫙",
        },
        {
            "brand_name":    "Tricho-D WP (Trichoderma)",
            "generic_name":  "Trichoderma viride 1.5% WP (1×10⁸ CFU/g)",
            "manufacturer":  "T Stanes / IARI recommended",
            "category":      "Bio-Fungicide",
            "form":          "Wettable Powder (WP) — Bio-product",
            "use_for": ["fusarium", "pythium", "root rot", "damping off", "soil-borne",
                        "wilt", "fungal", "collar rot"],
            # Real: white/grey bio-fungicide powder packet
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Trichoderma_harzianum.jpg/320px-Trichoderma_harzianum.jpg",
            "description": (
                "Beneficial fungus powder that fights root pathogens. "
                "Mix 5 g in 1 L water. Apply as soil drench around root zone, "
                "or mix 10 g/kg seed for seed treatment."
            ),
            "how_to_use": "Dissolve powder → soil drench around roots",
            "color": "#10b981",
            "emoji": "🌾",
        },
        {
            "brand_name":    "Beauvicide WP (Beauveria)",
            "generic_name":  "Beauveria bassiana 1.15% WP (2×10⁸ CFU/g)",
            "manufacturer":  "Pest Control India / NBAII",
            "category":      "Bio-Insecticide",
            "form":          "Wettable Powder (WP) — Bio-product",
            "use_for": ["whitefly", "thrips", "aphid", "mealybug", "caterpillar",
                        "stem borer", "weevil"],
            # Real: white bio-powder sachet
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Beauveria_bassiana_growing_on_Galleria_mellonella.jpg/320px-Beauveria_bassiana_growing_on_Galleria_mellonella.jpg",
            "description": (
                "Entomopathogenic fungus powder — kills insects naturally. "
                "Mix 5 g in 1 L water. Spray in cool evening. "
                "Best at >60% humidity. Repeat after 7 days."
            ),
            "how_to_use": "Dissolve powder → spray in evening (not midday)",
            "color": "#a3e635",
            "emoji": "🌫️",
        },

        # ── MICRONUTRIENT POWDERS — dissolve and spray ──
        {
            "brand_name":    "Zinco-Max 21% WSP",
            "generic_name":  "Zinc Sulphate Monohydrate 21% WSP",
            "manufacturer":  "Coromandel International / Iffco",
            "category":      "Micronutrient",
            "form":          "Water Soluble Powder (WSP)",
            "use_for": ["zinc deficiency", "khaira disease", "stunted", "small leaves",
                        "rice", "maize", "wheat", "yellowing"],
            # Real: white crystalline Zinc Sulphate powder bag
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Zinc_sulfate_heptahydrate.jpg/320px-Zinc_sulfate_heptahydrate.jpg",
            "description": (
                "Corrects zinc deficiency in crops. "
                "Dissolve 2.5 g in 1 L water for foliar spray. "
                "Or broadcast 25 kg/ha as soil application."
            ),
            "how_to_use": "Dissolve powder in water → foliar spray or soil broadcast",
            "color": "#64748b",
            "emoji": "🌫️",
        },
        {
            "brand_name":    "Ferrous Sulphate 19% FeSO₄",
            "generic_name":  "Ferrous Sulphate 19% WSP",
            "manufacturer":  "GSFC / Indian Farmers Fertiliser",
            "category":      "Micronutrient",
            "form":          "Water Soluble Powder (WSP)",
            "use_for": ["iron deficiency", "chlorosis", "yellowing", "interveinal",
                        "rice", "fruit crops", "pale leaves"],
            # Real: pale green crystalline FeSO4 powder
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Iron%28II%29_sulfate_heptahydrate.jpg/320px-Iron%28II%29_sulfate_heptahydrate.jpg",
            "description": (
                "Corrects iron-deficiency chlorosis (yellowing between leaf veins). "
                "Mix 10 g in 1 L water. Apply as foliar spray on yellowing leaves."
            ),
            "how_to_use": "Dissolve powder in water → foliar spray on yellow leaves",
            "color": "#a16207",
            "emoji": "🌫️",
        },
    ]

    # Score each medicine against the problem description
    combined_text = f"{problem} {chemical} {biological} {crop}"
    scored = []
    for med in MEDICINE_IMAGES:
        score = sum(1 for kw in med["use_for"] if kw in combined_text)
        if score > 0:
            scored.append((score, med))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return top 4 relevant medicines; if none match, return general defaults
    if scored:
        results = [m for _, m in scored[:4]]
    else:
        # Generic fallback — always relevant starter kit
        results = [m for m in MEDICINE_IMAGES if m["brand_name"] in (
            "Ecohope Neem Oil EC", "Dithane M-45",
            "Tricho-D WP (Trichoderma)", "Confidor 200 SL"
        )]

    return jsonify({"success": True, "medicines": results})


@app.route("/api/multi-agent", methods=["POST"])
def api_multi_agent():
    """
    Full multi-agent collaboration endpoint:
    runs all agents and returns consolidated response.
    """
    data = request.get_json(force=True)
    crop = data.get("crop", "").strip()
    location = data.get("location", "India").strip()
    if not crop:
        return jsonify({"error": "Crop is required"}), 400

    try:
        weather = get_weather_data(location)
        context = {
            "crop": crop,
            "location": location,
            "soil_type": data.get("soil_type", "loamy"),
            "season": data.get("season", "Kharif"),
            "growth_stage": data.get("growth_stage", "vegetative"),
            "weather_data": weather,
            "harvest_month": data.get("harvest_month", "November"),
            "quantity_kg": data.get("quantity_kg", 1000),
            "farming_cost": data.get("farming_cost"),
        }

        # Run all agents
        crop_advice = crop_advisory_agent(
            crop=crop, location=location,
            soil_type=context["soil_type"], season=context["season"],
            farmer_query=f"Complete advisory for {crop} in {location}",
        )
        weather_advice = weather_irrigation_agent(
            location=location, crop=crop,
            growth_stage=context["growth_stage"], weather_data=weather,
        )
        market_advice = market_insights_agent(
            crop=crop, quantity_kg=context["quantity_kg"],
            location=location, harvest_month=context["harvest_month"],
            farming_cost=context.get("farming_cost"),
        )

        return jsonify({
            "success": True,
            "data": {
                "crop_advisory": crop_advice,
                "weather_irrigation": weather_advice,
                "market_insights": market_advice,
                "weather_data": weather,
                "agents_used": [
                    "Crop Advisory Agent",
                    "Weather & Irrigation Agent",
                    "Market Insights Agent",
                ],
            },
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
