"""
Multi-Agent System for Smart Farming
Each agent is a specialized AI module powered by Groq LLM
Falls back to rich demo responses when no API key is configured.
"""
import json
import base64
from config import Config
from knowledge_base.farming_kb import search_knowledge_base

# ─────────────────────────────────────────────
# API client setup — only init if key is valid
# ─────────────────────────────────────────────
_API_KEY_VALID = (
    Config.GROQ_API_KEY
    and Config.GROQ_API_KEY.strip()
    and Config.GROQ_API_KEY != "your_groq_api_key_here"
)

_groq_client = None
if _API_KEY_VALID:
    try:
        from groq import Groq
        _groq_client = Groq(api_key=Config.GROQ_API_KEY)
    except Exception:
        _groq_client = None

MODEL = Config.GROQ_MODEL


def _chat(messages: list, temperature: float = 0.4, max_tokens: int = 1200) -> str:
    """Core Groq chat completion call."""
    if _groq_client is None:
        raise RuntimeError("GROQ_API_KEY is not configured. Add your key to the .env file.")
    response = _groq_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _demo_mode() -> bool:
    """Returns True when running without a valid API key."""
    return _groq_client is None


# ─────────────────────────────────────────────
# DEMO / FALLBACK RESPONSES
# ─────────────────────────────────────────────

def _demo_crop_advisory(crop: str, location: str, soil_type: str, season: str) -> dict:
    return {
        "summary": (
            f"Based on your {season} season conditions in {location} with {soil_type} soil, "
            f"{crop} cultivation looks promising. Follow the structured plan below for optimal yield."
        ),
        "seed_recommendation": (
            f"Use certified high-yielding varieties suited to {location}. "
            "For rice: IR-64, Swarna; for wheat: HD-2967, PBW-343; for tomato: Pusa Ruby, Arka Vikas. "
            "Purchase seeds from government-recognized seed companies to ensure germination rate > 90%."
        ),
        "fertilizer_schedule": (
            "Basal dose (at sowing): 50% N + full P + full K. "
            "Top dressing 1 (30 days): 25% N. "
            "Top dressing 2 (60 days): 25% N. "
            "Typical NPK: 120:60:60 kg/ha for cereals; 80:40:40 kg/ha for vegetables. "
            "Add 10 tonnes FYM/ha two weeks before sowing."
        ),
        "irrigation_plan": (
            "Critical irrigation stages: (1) germination/transplanting, (2) tillering/branching, "
            "(3) flowering, (4) grain/fruit filling. "
            "Drip irrigation recommended — saves 40-50% water. "
            "Irrigate when soil moisture drops to 50% field capacity."
        ),
        "harvesting_timeline": (
            f"Expected harvest: 90–120 days from sowing for most {crop} varieties. "
            "Harvest when grains reach 14% moisture (cereals) or fruits show mature colour (vegetables). "
            "Early morning harvesting reduces post-harvest losses."
        ),
        "key_warnings": [
            "Conduct soil pH test before sowing; ideal range 6.0–7.0",
            "Use disease-resistant certified seed varieties",
            "Watch for early signs of pest infestation after crop establishment",
            "Avoid waterlogging — ensure proper field drainage",
            "Store harvested produce at correct temperature and humidity",
        ],
        "tips": [
            "Apply neem cake at 250 kg/ha to suppress soil-borne pathogens",
            "Use pheromone traps (5/acre) for pest monitoring",
            "Practice intercropping to maximize land productivity",
            "Register for PM-KISAN and PMFBY crop insurance before cutoff",
            "Maintain farm diary for input costs and yield tracking",
        ],
        "_demo": True,
        "_note": "Demo response — add GROQ_API_KEY to .env for AI-powered personalized advisory",
    }


def _demo_weather_irrigation(location: str, crop: str, growth_stage: str, weather_data: dict) -> dict:
    temp = weather_data.get("current", {}).get("temperature", 28) if weather_data else 28
    humidity = weather_data.get("current", {}).get("humidity", 72) if weather_data else 72
    return {
        "weather_summary": (
            f"Current conditions in {location}: {temp}°C, {humidity}% humidity — "
            "typical for this time of year. Conditions are suitable for field operations. "
            "No extreme weather events forecast in the next 5 days."
        ),
        "irrigation_recommendation": {
            "next_irrigation_date": "2–3 days from today",
            "water_amount_mm": 35,
            "method": "Drip irrigation" if "vegetative" in growth_stage.lower() else "Sprinkler",
            "frequency": "Every 3–4 days during vegetative stage; every 2 days during flowering"
        },
        "field_actions": [
            f"Apply top-dress nitrogen fertilizer — {crop} at {growth_stage} stage needs it",
            "Check drip emitters and filter screens for clogging",
            "Scout for aphids and whitefly on leaf undersides",
            "Remove weeds from inter-rows to reduce competition",
            "Apply mulch to conserve soil moisture between irrigations",
        ],
        "risk_alerts": [
            "High humidity (>75%) increases fungal disease risk — spray preventive fungicide",
            "Wind speed may affect sprinkler efficiency — irrigate in early morning",
            "Monitor soil moisture with tensiometer if available",
        ],
        "forecast_advice": (
            "Next 5 days look dry and warm — plan 2 irrigation cycles. "
            "If rain is forecast, hold irrigation 24 hours before. "
            "Maintain good air circulation in crop canopy to prevent disease."
        ),
        "_demo": True,
        "_note": "Demo response — add GROQ_API_KEY to .env for AI-powered irrigation scheduling",
    }


def _demo_pest_disease(crop: str, symptoms: str, location: str) -> dict:
    return {
        "identified_problem": "Likely Fungal Leaf Blight or Aphid Infestation",
        "confidence": "Medium",
        "severity": "Moderate",
        "description": (
            f"Based on the described symptoms on {crop} in {location}, "
            "the most common culprits are fungal leaf blight (Alternaria/Helminthosporium) "
            "or early-stage aphid colony establishment. Both are common during humid conditions."
        ),
        "symptoms_match": [
            "Yellow or brown spots on leaves",
            "Wilting or curling of leaf edges",
            "Presence of small insects on leaf undersides",
            "Stunted growth or reduced vigor",
        ],
        "immediate_action": (
            "1) Remove and destroy heavily infected plant parts. "
            "2) Spray Mancozeb 2.5 g/L + Neem oil 3 ml/L mixture today. "
            "3) Improve air circulation by thinning dense crop canopy."
        ),
        "chemical_treatment": {
            "product": "Mancozeb 75% WP (fungal) OR Imidacloprid 17.8% SL (insects)",
            "dose": "Mancozeb: 2.5 g/L water | Imidacloprid: 0.3 ml/L water",
            "frequency": "Every 7–10 days, max 3 sprays per season"
        },
        "biological_treatment": (
            "Spray Trichoderma viride (5g/L) for fungal control. "
            "Release Chrysoperla carnea (green lacewing) for aphid biological control. "
            "Neem oil 3 ml/L + garlic extract 10 ml/L as eco-friendly option."
        ),
        "preventive_measures": [
            "Use disease-free certified seeds from reliable sources",
            "Avoid overhead irrigation — use drip to keep foliage dry",
            "Maintain proper plant spacing for air circulation",
            "Rotate crops — avoid same family in same field for 2 seasons",
            "Apply copper oxychloride 3 g/L as preventive spray at onset of humid weather",
        ],
        "spread_risk": (
            "Moderate to High — fungal spores spread via wind and water splash. "
            "Aphids can double population in 7–10 days. Act within 48 hours."
        ),
        "_demo": True,
        "_note": "Demo response — add GROQ_API_KEY to .env for AI-powered diagnosis",
    }


def _demo_market_insights(crop: str, quantity_kg: float, location: str, harvest_month: str, farming_cost: float) -> dict:
    est_price = 2500
    profit = None
    if farming_cost:
        revenue = (quantity_kg / 100) * est_price  # quintals × price
        profit = f"Rs {revenue - farming_cost:,.0f} estimated profit (revenue Rs {revenue:,.0f} - cost Rs {farming_cost:,.0f})"
    return {
        "current_price_estimate": {
            "min_rs_per_quintal": 2000,
            "max_rs_per_quintal": 3200,
            "trend": "stable"
        },
        "forecast_at_harvest": {
            "expected_price_rs_per_quintal": est_price,
            "market_outlook": (
                f"{crop} prices in {harvest_month} are typically stable. "
                "Festive season demand boosts vegetable prices by 15–20%. "
                "Monitor e-NAM portal for real-time price discovery."
            )
        },
        "selling_strategy": (
            f"For {quantity_kg} kg of {crop} in {location}: "
            "1) Store 30% of produce and sell during lean season for premium. "
            "2) Sell 50% immediately post-harvest to cover input costs. "
            "3) Process remaining 20% (dry/pickle/puree) for 50-100% value addition. "
            "Register with nearest APMC mandi or e-NAM portal for best prices."
        ),
        "best_markets": [
            "Local APMC mandi for immediate sale",
            "e-NAM online platform for wider buyer reach",
            "Direct supply to supermarkets/retailers (20-30% premium)",
            "FPO (Farmer Producer Organization) collective marketing",
            "Food processing companies for contract farming agreements",
        ],
        "value_addition_options": [
            "Grading and sorting improves market price by 20-30%",
            "Cold storage extends shelf life and allows off-season sale",
            "Processing into value-added products (paste, powder, chips)",
            "Organic certification commands 20-50% premium",
            "Attractive packaging with QR code for traceability",
        ],
        "cost_optimization": [
            "Soil testing prevents over-application of fertilizers (saves 15-20%)",
            "Custom hiring of machinery reduces equipment costs",
            "Group purchase of inputs through FPO for bulk discount",
            "Precision irrigation reduces water and energy costs",
            "Integrated pest management reduces pesticide spend by 30%",
        ],
        "profit_estimate": profit or "Provide farming cost for profit estimate",
        "government_schemes": [
            "PM-KISAN: Rs 6,000/year direct income support",
            "PMFBY: Crop insurance at 2% premium (Kharif)",
            "e-NAM: Online market platform for direct selling",
            "PM Krishi Sinchai Yojana: Drip irrigation subsidy 55-90%",
            "Soil Health Card scheme: Free soil testing",
        ],
        "risk_factors": [
            "Price crash during peak harvest season — plan staggered selling",
            "Post-harvest losses from poor storage — invest in cold chain",
            "Weather events affecting supply and demand dynamics",
            "Import policy changes for competing commodities",
        ],
        "_demo": True,
        "_note": "Demo response — add GROQ_API_KEY to .env for AI-powered market intelligence",
    }


def _demo_master_agent(user_query: str, context: dict) -> dict:
    crop = context.get("crop", "rice")
    location = context.get("location", "India")
    return {
        "query": user_query,
        "intent": {
            "intents": ["general"],
            "primary_intent": "general",
            "extracted_info": {"crop": crop, "location": location}
        },
        "agents_used": ["General Farming Assistant (Demo)"],
        "general_advice": (
            f"🌾 Smart Farming Advisory for: '{user_query}'\n\n"
            "Here are key recommendations based on best agricultural practices:\n\n"
            "1. **Soil Preparation**: Test soil pH (ideal 6.0–7.5) and add organic matter (10 t/ha FYM) before planting.\n\n"
            "2. **Seed Selection**: Use certified high-yielding varieties from government-approved sources. "
            "Treat seeds with Trichoderma or Bavistin before sowing.\n\n"
            "3. **Nutrient Management**: Follow soil-test-based fertilizer recommendations. "
            "Split nitrogen application reduces losses and improves uptake.\n\n"
            "4. **Water Management**: Adopt drip/sprinkler irrigation to save 40-50% water. "
            "Irrigate at critical crop growth stages.\n\n"
            "5. **Pest & Disease**: Scout fields twice weekly. Use IPM approach — "
            "biological controls first, chemical as last resort.\n\n"
            "6. **Market Linkage**: Register on e-NAM portal, join FPO for collective bargaining. "
            "Enroll in PMFBY crop insurance before cutoff.\n\n"
            "📌 Add your GROQ_API_KEY in the .env file for personalized AI-powered advice."
        ),
        "_demo": True,
        "_note": "Demo mode — configure GROQ_API_KEY in .env for full AI capabilities",
    }


# ─────────────────────────────────────────────
# AGENT 1 — Crop Advisory Agent
# ─────────────────────────────────────────────
def crop_advisory_agent(
    crop: str,
    location: str,
    soil_type: str,
    season: str,
    farmer_query: str,
) -> dict:
    """
    Retrieves crop-specific guidelines from the knowledge base (RAG)
    and generates personalized advisory using the LLM.
    Falls back to structured demo response when API key is unavailable.
    """
    if _demo_mode():
        return _demo_crop_advisory(crop, location, soil_type, season)

    # RAG retrieval
    rag_docs = search_knowledge_base(
        f"{crop} {farmer_query} {soil_type}", category=None, top_k=3
    )
    rag_context = "\n\n".join(
        f"[{d['title']}]\n{d['content']}" for d in rag_docs
    )

    system_prompt = """You are an expert Crop Advisory Agent with deep knowledge in agronomy and sustainable agriculture.
Using the retrieved knowledge base excerpts and your expertise, provide structured, actionable advice.
Format your response as JSON with these keys:
{
  "summary": "2-3 sentence overview",
  "seed_recommendation": "best varieties for the conditions",
  "fertilizer_schedule": "NPK and organic inputs schedule",
  "irrigation_plan": "watering frequency and method",
  "harvesting_timeline": "expected timeline and indicators",
  "key_warnings": ["list of critical warnings"],
  "tips": ["list of 3-5 actionable tips"]
}"""

    user_msg = f"""
Farmer Query: {farmer_query}
Crop: {crop}
Location: {location}
Soil Type: {soil_type}
Season: {season}

Retrieved Knowledge Base Context:
{rag_context}

Provide personalized crop advisory in the specified JSON format.
"""
    raw = _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ])

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except Exception:
        return {"summary": raw, "raw": True}


# ─────────────────────────────────────────────
# AGENT 2 — Weather & Irrigation Agent
# ─────────────────────────────────────────────
def weather_irrigation_agent(
    location: str,
    crop: str,
    growth_stage: str,
    weather_data: dict,
) -> dict:
    """
    Analyses weather data and generates irrigation & field management advice.
    Falls back to structured demo response when API key is unavailable.
    """
    if _demo_mode():
        return _demo_weather_irrigation(location, crop, growth_stage, weather_data)

    system_prompt = """You are a Weather & Irrigation Intelligence Agent specializing in precision agriculture.
Analyze the provided weather data and crop growth stage to give irrigation scheduling advice.
Return structured JSON:
{
  "weather_summary": "current conditions analysis",
  "irrigation_recommendation": {
    "next_irrigation_date": "date or days from now",
    "water_amount_mm": number,
    "method": "drip/sprinkler/flood",
    "frequency": "schedule description"
  },
  "field_actions": ["list of immediate field actions"],
  "risk_alerts": ["weather-related risks and mitigation"],
  "forecast_advice": "5-day planning advice"
}"""

    weather_str = json.dumps(weather_data, indent=2) if weather_data else "Weather data unavailable - use seasonal averages"

    user_msg = f"""
Location: {location}
Crop: {crop}
Growth Stage: {growth_stage}
Weather Data: {weather_str}

Provide irrigation scheduling and weather-based field management advice.
"""
    raw = _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ])

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except Exception:
        return {"weather_summary": raw, "raw": True}


# ─────────────────────────────────────────────
# AGENT 3 — Pest & Disease Detection Agent
# ─────────────────────────────────────────────
def pest_disease_agent(
    crop: str,
    symptoms: str,
    location: str,
    image_base64: str = None,
) -> dict:
    """
    Identifies pest/disease from symptoms description and optional image,
    returns treatment recommendations.
    Falls back to structured demo response when API key is unavailable.
    """
    if _demo_mode():
        return _demo_pest_disease(crop, symptoms, location)

    # RAG retrieval for pest context
    rag_docs = search_knowledge_base(
        f"{crop} pest disease {symptoms}", category="pest_disease", top_k=2
    )
    rag_context = "\n\n".join(
        f"[{d['title']}]\n{d['content']}" for d in rag_docs
    )

    system_prompt = """You are an expert Plant Pathologist and Pest Management Specialist.
Identify the pest/disease from the symptoms and provide treatment protocol.
Return structured JSON:
{
  "identified_problem": "name of pest/disease/deficiency",
  "confidence": "High/Medium/Low",
  "severity": "Mild/Moderate/Severe",
  "description": "what this problem is",
  "symptoms_match": ["observed symptoms that match"],
  "immediate_action": "do this TODAY",
  "chemical_treatment": {
    "product": "recommended chemical",
    "dose": "application dose",
    "frequency": "how often to apply"
  },
  "biological_treatment": "eco-friendly alternatives",
  "preventive_measures": ["list of prevention steps"],
  "spread_risk": "how quickly it can spread"
}"""

    user_msg = f"""
Crop: {crop}
Location: {location}
Observed Symptoms: {symptoms}

Relevant Knowledge Base:
{rag_context}

{"[Image analysis requested - describe visual symptoms visible in the image]" if image_base64 else ""}

Identify the problem and provide treatment protocol.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add image if provided (vision capability)
    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
                {"type": "text", "text": user_msg},
            ],
        })
    else:
        messages.append({"role": "user", "content": user_msg})

    # Use vision model if image present
    if image_base64:
        try:
            from groq import Groq
            response = _groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=messages,
                temperature=0.3,
                max_tokens=1200,
            )
            raw = response.choices[0].message.content.strip()
        except Exception:
            raw = _chat([{"role": "system", "content": system_prompt},
                         {"role": "user", "content": user_msg}])
    else:
        raw = _chat(messages)

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except Exception:
        return {"identified_problem": raw, "raw": True}


# ─────────────────────────────────────────────
# AGENT 4 — Market Insights Agent
# ─────────────────────────────────────────────
def market_insights_agent(
    crop: str,
    quantity_kg: float,
    location: str,
    harvest_month: str,
    farming_cost: float = None,
) -> dict:
    """
    Provides market price forecasts, selling strategy, and cost optimization advice.
    Falls back to structured demo response when API key is unavailable.
    """
    if _demo_mode():
        return _demo_market_insights(crop, quantity_kg, location, harvest_month, farming_cost)

    rag_docs = search_knowledge_base(
        f"{crop} market price value addition", category="market", top_k=2
    )
    rag_context = "\n\n".join(
        f"[{d['title']}]\n{d['content']}" for d in rag_docs
    )

    system_prompt = """You are an Agricultural Market Intelligence and Economics Expert.
Provide market price forecasts and selling strategy recommendations.
Return structured JSON:
{
  "current_price_estimate": {
    "min_rs_per_quintal": number,
    "max_rs_per_quintal": number,
    "trend": "rising/stable/falling"
  },
  "forecast_at_harvest": {
    "expected_price_rs_per_quintal": number,
    "market_outlook": "description"
  },
  "selling_strategy": "when and how to sell",
  "best_markets": ["list of market types/channels"],
  "value_addition_options": ["processing/packaging opportunities"],
  "cost_optimization": ["ways to reduce production costs"],
  "profit_estimate": "estimated profit per hectare if farming cost provided",
  "government_schemes": ["relevant subsidies and schemes"],
  "risk_factors": ["market risks to watch"]
}"""

    cost_info = f"\nFarming cost so far: Rs {farming_cost}/ha" if farming_cost else ""
    user_msg = f"""
Crop: {crop}
Quantity Available: {quantity_kg} kg
Location: {location}
Expected Harvest Month: {harvest_month}{cost_info}

Market Knowledge Base:
{rag_context}

Provide market forecast and selling strategy.
"""

    raw = _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ])

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except Exception:
        return {"selling_strategy": raw, "raw": True}


# ─────────────────────────────────────────────
# ORCHESTRATOR — Master Farming Agent
# ─────────────────────────────────────────────
def master_farming_agent(user_query: str, context: dict = None) -> dict:
    """
    Orchestrates all sub-agents based on user intent and returns
    a comprehensive, consolidated farming advisory.
    Falls back to demo mode when API key is unavailable.
    """
    context = context or {}

    if _demo_mode():
        return _demo_master_agent(user_query, context)

    # Step 1: Classify intent
    intent_prompt = """Classify this farming query into one or more categories.
Return JSON: {"intents": ["crop_advisory", "weather_irrigation", "pest_disease", "market_insights", "general"], "primary_intent": "...", "extracted_info": {"crop": "...", "location": "...", "issue": "..."}}
Only return JSON, no explanation."""

    intent_raw = _chat([
        {"role": "system", "content": intent_prompt},
        {"role": "user", "content": user_query},
    ], temperature=0.1, max_tokens=300)

    try:
        clean = intent_raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        intent = json.loads(clean)
    except Exception:
        intent = {"intents": ["general"], "primary_intent": "general", "extracted_info": {}}

    extracted = intent.get("extracted_info", {})
    crop = context.get("crop") or extracted.get("crop", "general crop")
    location = context.get("location") or extracted.get("location", "India")

    results = {"query": user_query, "intent": intent, "agents_used": []}

    # Step 2: Route to relevant agents
    primary = intent.get("primary_intent", "general")
    intents = intent.get("intents", ["general"])

    if "crop_advisory" in intents:
        results["crop_advisory"] = crop_advisory_agent(
            crop=crop,
            location=location,
            soil_type=context.get("soil_type", "loamy"),
            season=context.get("season", "Kharif"),
            farmer_query=user_query,
        )
        results["agents_used"].append("Crop Advisory Agent")

    if "weather_irrigation" in intents:
        results["weather_irrigation"] = weather_irrigation_agent(
            location=location,
            crop=crop,
            growth_stage=context.get("growth_stage", "vegetative"),
            weather_data=context.get("weather_data", {}),
        )
        results["agents_used"].append("Weather & Irrigation Agent")

    if "pest_disease" in intents:
        results["pest_disease"] = pest_disease_agent(
            crop=crop,
            symptoms=extracted.get("issue", user_query),
            location=location,
            image_base64=context.get("image_base64"),
        )
        results["agents_used"].append("Pest & Disease Agent")

    if "market_insights" in intents:
        results["market_insights"] = market_insights_agent(
            crop=crop,
            quantity_kg=context.get("quantity_kg", 1000),
            location=location,
            harvest_month=context.get("harvest_month", "November"),
            farming_cost=context.get("farming_cost"),
        )
        results["agents_used"].append("Market Insights Agent")

    # Fallback for general queries
    if not results["agents_used"] or primary == "general":
        general_resp = _chat([
            {"role": "system", "content": "You are a knowledgeable Smart Farming AI Assistant. Provide helpful, accurate, and practical farming advice. Be concise but thorough."},
            {"role": "user", "content": user_query},
        ], max_tokens=800)
        results["general_advice"] = general_resp
        results["agents_used"].append("General Farming Assistant")

    # Step 3: Synthesize a final summary
    if len(results["agents_used"]) > 1:
        agent_outputs = {k: v for k, v in results.items()
                        if k not in ("query", "intent", "agents_used")}
        synthesis_msg = f"""
Based on the following multi-agent analysis for the query: "{user_query}"

{json.dumps(agent_outputs, indent=2)[:3000]}

Write a concise executive summary (3-5 sentences) that ties together the key actionable insights for the farmer.
"""
        results["executive_summary"] = _chat([
            {"role": "system", "content": "You are a Smart Farming Advisor. Synthesize multi-agent outputs into a clear farmer-friendly summary."},
            {"role": "user", "content": synthesis_msg},
        ], max_tokens=400)

    return results
