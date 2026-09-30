from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from google import genai
from PIL import Image
from dotenv import load_dotenv
import os
import io

load_dotenv()

# -----------------------------
# Gemini Configuration
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="PocketSmart AI")

templates = Jinja2Templates(directory="templates")


# -----------------------------
# Gemini Helper
# -----------------------------
def generate_with_gemini(prompt: str):
    if not client:
        return None

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if response and response.text:
            return response.text

    except Exception:
        return None

    return None


# -----------------------------
# Home Budget Fallback
# -----------------------------
def home_fallback(budget: int, rooms: str):

    furniture = int(budget * 0.40)
    lighting = int(budget * 0.15)
    storage = int(budget * 0.15)
    decoration = int(budget * 0.15)
    miscellaneous = budget - (
        furniture + lighting + storage + decoration
    )

    return f"""
HOME INTERIOR BUDGET PLAN
=========================

Total Budget: ₹{budget:,}

Rooms / Items:
{rooms}


1. FURNITURE
Budget: ₹{furniture:,}

Suggested:
• Sofa / Seating
• Bed / Storage
• Tables
• Basic furniture


2. LIGHTING
Budget: ₹{lighting:,}

Suggested:
• Ceiling lights
• LED lights
• Table lamps
• Decorative lights


3. STORAGE
Budget: ₹{storage:,}

Suggested:
• Shelves
• Organizers
• Cabinets


4. DECORATION
Budget: ₹{decoration:,}

Suggested:
• Curtains
• Rugs
• Wall decoration
• Indoor plants


5. MISCELLANEOUS
Budget: ₹{miscellaneous:,}

Suggested:
• Installation
• Small accessories
• Emergency expenses


Suggested Shopping Platforms:
• IKEA
• Amazon
• Flipkart
"""


# -----------------------------
# Party Budget Fallback
# -----------------------------
def party_fallback(budget: int, guests: int, event_type: str):

    food = int(budget * 0.40)
    venue = int(budget * 0.20)
    decoration = int(budget * 0.15)
    entertainment = int(budget * 0.10)
    miscellaneous = budget - (
        food + venue + decoration + entertainment
    )

    return f"""
PARTY BUDGET PLAN
=================

Event Type: {event_type}

Guests: {guests}

Total Budget: ₹{budget:,}


1. FOOD & DRINKS
Budget: ₹{food:,}

Suggested:
• Main food
• Snacks
• Soft drinks
• Desserts


2. VENUE
Budget: ₹{venue:,}

Suggested:
• Hall / Event space
• Seating
• Basic arrangements


3. DECORATION
Budget: ₹{decoration:,}

Suggested:
• Balloons
• Banners
• Table decoration
• Lights


4. ENTERTAINMENT
Budget: ₹{entertainment:,}

Suggested:
• Music
• Games
• Activities


5. MISCELLANEOUS
Budget: ₹{miscellaneous:,}

Suggested:
• Invitations
• Transportation
• Emergency expenses


Suggested Platforms:
• Amazon
• Flipkart
• Local event stores
"""


# -----------------------------
# Jewelry Budget Fallback
# -----------------------------
def jewelry_fallback(budget: int, jewelry_type: str):

    jewelry_cost = int(budget * 0.80)
    making = int(budget * 0.10)
    miscellaneous = budget - jewelry_cost - making

    return f"""
JEWELRY BUDGET PLAN
===================

Jewelry Type: {jewelry_type}

Total Budget: ₹{budget:,}


1. JEWELRY
Budget: ₹{jewelry_cost:,}

Suggested:
• Choose the required jewelry style
• Compare different designs
• Check available materials
• Compare prices before purchase


2. MAKING / SERVICE CHARGES
Budget: ₹{making:,}

Suggested:
• Making charges
• Customization
• Finishing


3. MISCELLANEOUS
Budget: ₹{miscellaneous:,}

Suggested:
• Packaging
• Additional services
• Other small expenses


Shopping Suggestions:
• Local jewelry stores
• Trusted online jewelry stores
• Compare multiple sellers
"""


# -----------------------------
# Home Page
# -----------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# -----------------------------
# Home Budget Page
# -----------------------------
@app.get("/home-budget")
def home_budget_page(request: Request):
    return templates.TemplateResponse(
        "home_budget.html",
        {"request": request}
    )


# -----------------------------
# Home Budget API
# -----------------------------
@app.post("/api/home-budget")
def home_budget_api(
    budget: int = Form(...),
    rooms: str = Form(...)
):

    prompt = f"""
Create a detailed home interior budget recommendation.

Budget: ₹{budget}
Rooms: {rooms}

Give:
1. Furniture
2. Lighting
3. Storage
4. Decoration
5. Miscellaneous

Include budget amounts and practical suggestions.
"""

    recommendation = generate_with_gemini(prompt)

    if not recommendation:
        recommendation = home_fallback(
            budget,
            rooms
        )

    return {
        "success": True,
        "recommendation": recommendation
    }


# -----------------------------
# Party Budget Page
# -----------------------------
@app.get("/party-budget")
def party_budget_page(request: Request):
    return templates.TemplateResponse(
        "party_budget.html",
        {"request": request}
    )


# -----------------------------
# Party Budget API
# -----------------------------
@app.post("/api/party-budget")
def party_budget_api(
    budget: int = Form(...),
    guests: int = Form(...),
    event_type: str = Form(...)
):

    prompt = f"""
Create a detailed party budget recommendation.

Total Budget: ₹{budget}
Guests: {guests}
Event Type: {event_type}

Include:
1. Food
2. Venue
3. Decoration
4. Entertainment
5. Miscellaneous

Give practical budget amounts.
"""

    recommendation = generate_with_gemini(prompt)

    if not recommendation:
        recommendation = party_fallback(
            budget,
            guests,
            event_type
        )

    return {
        "success": True,
        "recommendation": recommendation
    }


# -----------------------------
# Jewelry Page
# -----------------------------
@app.get("/jewelry")
def jewelry_page(request: Request):
    return templates.TemplateResponse(
        "jewelry.html",
        {"request": request}
    )


# -----------------------------
# Jewelry Budget API
# -----------------------------
@app.post("/api/jewelry-budget")
async def jewelry_budget_api(
    budget: int = Form(...),
    jewelry_type: str = Form(...),
    image: UploadFile | None = File(None)
):

    image_info = ""

    if image:
        try:
            image_bytes = await image.read()

            img = Image.open(
                io.BytesIO(image_bytes)
            )

            image_info = (
                f"Image uploaded successfully. "
                f"Image size: {img.size}"
            )

        except Exception:
            image_info = ""

    prompt = f"""
Create a detailed jewelry budget recommendation.

Budget: ₹{budget}
Jewelry Type: {jewelry_type}

{image_info}

Give:
1. Jewelry budget
2. Making/service charges
3. Miscellaneous expenses
4. Shopping suggestions

Keep the recommendation practical.
"""

    recommendation = generate_with_gemini(prompt)

    if not recommendation:
        recommendation = jewelry_fallback(
            budget,
            jewelry_type
        )

    return {
        "success": True,
        "recommendation": recommendation
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "PocketSmart AI"
    }