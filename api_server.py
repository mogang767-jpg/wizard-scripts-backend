"""
FastAPI server for Wizard Scripts Telegram Mini App.

Serves:
- Static files (built React TMA)
- API endpoints for custom requests, leaderboard, user data
"""

import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import (
    init_db,
    create_custom_request,
    get_leaderboard,
    get_products,
    get_user,
    get_user_purchases,
    get_referral_count,
)
from config import ADMIN_ID, WEBAPP_URL

logger = logging.getLogger(__name__)

# --- Pydantic Models ---

class CustomRequestPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(default="", max_length=100)
    description: str = Field(..., min_length=10, max_length=5000)
    budget: str = Field(default="", max_length=50)
    deadline: str = Field(default="", max_length=50)
    userId: int = Field(default=0)


class UserDataResponse(BaseModel):
    id: int
    firstName: str
    lastName: str | None = None
    username: str | None = None
    languageCode: str = "ru"
    referralCount: int = 0


# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    logger.info("API Server database initialized")
    yield


# --- App Setup ---

app = FastAPI(
    title="Wizard Scripts API",
    description="Backend API for Wizard Scripts Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---

DIST_DIR = Path(__file__).parent / "dist"
if DIST_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(DIST_DIR), html=True), name="app")


# --- API Routes ---

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/user/{user_id}")
async def get_user_data(user_id: int):
    """Get user data including referral count."""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ref_count = await get_referral_count(user_id)

    return {
        "id": user["tg_id"],
        "firstName": user["first_name"] or "User",
        "lastName": user["last_name"],
        "username": user["username"],
        "languageCode": user["language_code"] or "ru",
        "referralCount": ref_count,
    }


@app.get("/api/products")
async def list_products():
    """Get all active products."""
    products = await get_products()
    return {
        "products": [
            {
                "id": p["id"],
                "key": p["product_key"],
                "name": p["name"],
                "description": p["description"],
                "price": p["price_stars"],
            }
            for p in products
        ]
    }


@app.get("/api/leaderboard")
async def leaderboard(limit: int = 10):
    """Get leaderboard data."""
    leaders = await get_leaderboard(limit)
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "name": l["username"] or l["first_name"] or "Anonymous",
                "purchases": l["purchases"],
                "spent": l["spent"],
            }
            for i, l in enumerate(leaders)
        ]
    }


@app.post("/api/custom-request")
async def submit_custom_request(payload: CustomRequestPayload):
    """Submit a custom development request."""
    try:
        request_id = await create_custom_request(
            user_id=payload.userId or 0,
            name=payload.name,
            username=payload.username,
            description=payload.description,
            budget=payload.budget,
            deadline=payload.deadline,
        )

        # Try to notify admin via bot if available
        try:
            from bot import bot
            from config import get_message

            if ADMIN_ID:
                lang = "ru"
                budget_str = payload.budget if payload.budget else "Не указан"
                deadline_str = payload.deadline if payload.deadline else "Не указан"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                admin_text = get_message(lang, "admin_notification").format(
                    name=payload.name,
                    username=payload.username or "N/A",
                    user_id=payload.userId or 0,
                    budget=budget_str,
                    deadline=deadline_str,
                    description=payload.description[:500],
                    timestamp=timestamp,
                )
                await bot.send_message(ADMIN_ID, admin_text)
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")

        return {
            "success": True,
            "requestId": request_id,
            "message": "Request submitted successfully",
        }

    except Exception as e:
        logger.error(f"Failed to create custom request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")


@app.get("/api/purchases/{user_id}")
async def get_purchases(user_id: int):
    """Get user's purchase history."""
    purchases = await get_user_purchases(user_id)
    return {
        "purchases": [
            {
                "id": p["id"],
                "productName": p["product_name"],
                "buyerId": p["buyer_id"],
                "amount": p["amount_stars"],
                "date": p["created_at"],
            }
            for p in purchases
        ]
    }


# --- Serve TMA ---

@app.get("/")
async def serve_tma():
    """Serve the Telegram Mini App."""
    index_path = DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(
        {"status": "API running", "message": "Build the frontend and copy to dist/"}
    )


@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve index.html for all routes (SPA routing)."""
    index_path = DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="Not found")


# --- Run Server ---

if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    uvicorn.run("api_server:app", host=HOST, port=PORT, reload=False)
