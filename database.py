"""
Database module for Wizard Scripts Bot.
Uses SQLite with aiosqlite for async operations.
"""

import aiosqlite
import secrets
import string
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

DB_PATH = Path(__file__).parent / "visual_scripts.db"


def generate_buyer_id() -> str:
    """Generate a cryptographically secure unique buyer ID."""
    alphabet = string.ascii_letters + string.digits
    return "VS-" + "".join(secrets.choice(alphabet) for _ in range(16))


async def init_db() -> None:
    """Initialize the database with all required tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'ru',
                referral_count INTEGER DEFAULT 0,
                referred_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referred_by) REFERENCES users(tg_id)
            )
            """
        )

        # Products table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price_stars INTEGER NOT NULL DEFAULT 120,
                file_id TEXT,
                file_path TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Purchases table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                buyer_id TEXT UNIQUE NOT NULL,
                amount_stars INTEGER NOT NULL DEFAULT 120,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(tg_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
        )

        # Custom requests table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                username TEXT,
                description TEXT NOT NULL,
                budget TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(tg_id)
            )
            """
        )

        await db.commit()

        # Seed products if empty
        cursor = await db.execute("SELECT COUNT(*) FROM products")
        count = await cursor.fetchone()
        if count and count[0] == 0:
            await seed_products(db)


async def seed_products(db: aiosqlite.Connection) -> None:
    """Seed default products into the database."""
    products = [
        ("automation", "\u0421\u043A\u0440\u0438\u043F\u0442 \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u0438", "\u0410\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u044F \u0440\u0443\u0442\u0438\u043D\u043D\u044B\u0445 \u0437\u0430\u0434\u0430\u0447", 120),
        ("parsing", "\u0421\u043A\u0440\u0438\u043F\u0442 \u043F\u0430\u0440\u0441\u0438\u043D\u0433\u0430", "\u0421\u0431\u043E\u0440 \u0434\u0430\u043D\u043D\u044B\u0445 \u0441 \u0432\u0435\u0431-\u0440\u0435\u0441\u0443\u0440\u0441\u043E\u0432", 120),
        ("chat", "\u0427\u0430\u0442-\u0431\u043E\u0442 \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440", "\u0423\u043C\u043D\u043E\u0435 \u0443\u043F\u0440\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0447\u0430\u0442\u0430\u043C\u0438", 120),
        ("trading", "\u0422\u0440\u0435\u0439\u0434\u0438\u043D\u0433 \u0431\u043E\u0442", "\u0410\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0430\u044F \u0442\u043E\u0440\u0433\u043E\u0432\u043B\u044F", 120),
        ("notify", "\u0421\u0438\u0441\u0442\u0435\u043C\u0430 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u0439", "\u041C\u0433\u043D\u043E\u0432\u0435\u043D\u043D\u044B\u0435 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F", 120),
        ("scheduler", "\u041F\u043B\u0430\u043D\u0438\u0440\u043E\u0432\u0449\u0438\u043A \u0437\u0430\u0434\u0430\u0447", "\u041F\u043B\u0430\u043D\u0438\u0440\u043E\u0432\u0430\u043D\u0438\u0435 \u0437\u0430\u0434\u0430\u0447", 120),
    ]
    await db.executemany(
        "INSERT INTO products (product_key, name, description, price_stars) VALUES (?, ?, ?, ?)",
        products,
    )
    await db.commit()


# --- User Operations ---

async def get_or_create_user(
    tg_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: Optional[str] = None,
    referred_by: Optional[int] = None,
) -> Dict[str, Any]:
    """Get existing user or create a new one."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        row = await cursor.fetchone()

        if row:
            user = dict(row)
            # Update user info if changed
            await db.execute(
                """
                UPDATE users SET
                    username = COALESCE(?, username),
                    first_name = COALESCE(?, first_name),
                    last_name = COALESCE(?, last_name),
                    language_code = COALESCE(?, language_code)
                WHERE tg_id = ?
                """,
                (username, first_name, last_name, language_code, tg_id),
            )
            await db.commit()
            return user

        # Create new user
        await db.execute(
            """
            INSERT INTO users (tg_id, username, first_name, last_name, language_code, referred_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (tg_id, username, first_name, last_name, language_code or "ru", referred_by),
        )

        # If referred_by is provided, increment referral count
        if referred_by:
            await db.execute(
                "UPDATE users SET referral_count = referral_count + 1 WHERE tg_id = ?",
                (referred_by,),
            )

        await db.commit()

        cursor = await db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        row = await cursor.fetchone()
        return dict(row) if row else {}


async def get_user(tg_id: int) -> Optional[Dict[str, Any]]:
    """Get user by Telegram ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_referral_count(tg_id: int) -> int:
    """Get the referral count for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT referral_count FROM users WHERE tg_id = ?", (tg_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


# --- Product Operations ---

async def get_products() -> List[Dict[str, Any]]:
    """Get all active products."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM products WHERE is_active = 1 ORDER BY id"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Get a single product by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_product_by_key(product_key: str) -> Optional[Dict[str, Any]]:
    """Get a product by its key."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM products WHERE product_key = ?", (product_key,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# --- Purchase Operations ---

async def create_purchase(user_id: int, product_id: int, amount_stars: int = 120) -> str:
    """Create a purchase record and return the unique buyer ID."""
    buyer_id = generate_buyer_id()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO purchases (user_id, product_id, buyer_id, amount_stars)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, product_id, buyer_id, amount_stars),
        )
        await db.commit()
    return buyer_id


async def get_user_purchases(user_id: int) -> List[Dict[str, Any]]:
    """Get all purchases for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT p.*, pr.name as product_name, pr.product_key
            FROM purchases p
            JOIN products pr ON p.product_id = pr.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_purchase_by_buyer_id(buyer_id: str) -> Optional[Dict[str, Any]]:
    """Get a purchase by buyer ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM purchases WHERE buyer_id = ?", (buyer_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# --- Leaderboard Operations ---

async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top buyers by purchase count."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT
                u.tg_id,
                u.username,
                u.first_name,
                COUNT(p.id) as purchases,
                COALESCE(SUM(p.amount_stars), 0) as spent
            FROM users u
            LEFT JOIN purchases p ON u.tg_id = p.user_id
            GROUP BY u.tg_id
            HAVING purchases > 0
            ORDER BY purchases DESC, spent DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# --- Custom Request Operations ---

async def create_custom_request(
    user_id: int,
    name: str,
    username: Optional[str],
    description: str,
    budget: Optional[str] = None,
    deadline: Optional[str] = None,
) -> int:
    """Create a custom request and return its ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO custom_requests (user_id, name, username, description, budget, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, username, description, budget, deadline),
        )
        await db.commit()
        return cursor.lastrowid or 0


async def get_pending_requests() -> List[Dict[str, Any]]:
    """Get all pending custom requests."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM custom_requests
            WHERE status = 'pending'
            ORDER BY created_at DESC
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_request_status(request_id: int, status: str) -> None:
    """Update the status of a custom request."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE custom_requests SET status = ? WHERE id = ?",
            (status, request_id),
        )
        await db.commit()
