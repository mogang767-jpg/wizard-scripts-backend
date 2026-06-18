# Visual Scripts — Telegram Bot & Mini App

A production-ready Telegram Bot and Telegram Mini App (TMA) for selling automated scripts. Built with **Python (Aiogram 3.x)** backend and **React + TypeScript** frontend.

---

## Features

### Frontend (Telegram Mini App)
- **High-end Minimalism**: Dark gray (#050505) background with neon green (#CCFF00) accents
- **Pure CSS/SVG**: No external image dependencies — all visuals built with code
- **Matrix Rain Animation**: Canvas-based digital rain effect in the hero section
- **Product Catalog**: 6 automation scripts, each priced at 120 Telegram Stars
- **Shopping Cart**: Add/remove items, view total, checkout
- **Referral System**: Track referrals via `?start=ref_userID` deep links
- **Leaderboard**: Dynamic table sorted by purchases or spending
- **Custom Request Form**: "\u0417\u0430\u043A\u0430\u0437\u0430\u0442\u044C \u043F\u043E \u0422\u0417" form that notifies admin
- **Multilingual**: Russian (default), English, Spanish with auto-detection

### Backend (Telegram Bot)
- **Aiogram 3.x**: Modern async Telegram Bot framework
- **FastAPI**: Web server for serving TMA and API endpoints
- **SQLite**: Lightweight local database
- **Payment Processing**: Telegram Stars payment via `send_invoice`
- **Automatic File Delivery**: Sends purchased script files after successful payment
- **Unique Buyer ID**: Cryptographically secure alphanumeric ID per transaction
- **Admin Notifications**: Instant alerts for purchases and custom requests
- **Referral Tracking**: Deep link parameter parsing and counter increment

---

## Project Structure

```
bot/
\u251C\u2500\u2500 bot.py              # Aiogram bot handlers
\u251C\u2500\u2500 api_server.py      # FastAPI server for TMA
\u251C\u2500\u2500 main.py             # Unified launcher (bot + API)
\u251C\u2500\u2500 database.py         # SQLite database operations
\u251C\u2500\u2500 config.py           # Configuration and i18n messages
\u251C\u2500\u2500 requirements.txt    # Python dependencies
\u251C\u2500\u2500 .env.example        # Environment variables template
\u251C\u2500\u2500 dist/               # Built TMA frontend files
\u2502   \u251C\u2500\u2500 index.html
\u2502   \u2514\u2500\u2500 assets/
\u2514\u2500\u2500 visual_scripts.db   # SQLite database (created at runtime)
```

---

## Quick Start

### 1. Configure Environment

```bash
cd bot
cp .env.example .env
```

Edit `.env` and set your values:
```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_telegram_user_id
WEBAPP_URL=https://your-deployed-tma-url.com
HOST=0.0.0.0
PORT=8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Run both bot and API server
python main.py

# Or run separately:
# Bot only
python bot.py

# API server only
python api_server.py
```

### 4. Set Up Telegram Bot

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Enable "Telegram Stars" payments
3. Set the Menu Button to open your Mini App:
   ```
   /setmenubutton
   ```
   Provide your `WEBAPP_URL`

---

## Database Schema

### users
| Column          | Type      | Description                        |
|-----------------|-----------|------------------------------------|
| id              | INTEGER   | Primary key                        |
| tg_id           | INTEGER   | Telegram user ID (unique)          |
| username        | TEXT      | Telegram username                  |
| first_name      | TEXT      | User's first name                  |
| last_name       | TEXT      | User's last name                   |
| language_code   | TEXT      | Preferred language (ru/en/es)      |
| referral_count  | INTEGER   | Number of referred users           |
| referred_by     | INTEGER   | Referrer's Telegram ID             |
| created_at      | TIMESTAMP | Registration timestamp             |

### products
| Column      | Type      | Description                    |
|-------------|-----------|--------------------------------|
| id          | INTEGER   | Primary key                    |
| product_key | TEXT      | Unique identifier (e.g., "automation") |
| name        | TEXT      | Display name                   |
| description | TEXT      | Product description            |
| price_stars | INTEGER   | Price in Telegram Stars (120)  |
| file_id     | TEXT      | Telegram file_id for delivery  |
| file_path   | TEXT      | Local file path (alternative)  |
| is_active   | BOOLEAN   | Whether product is available   |

### purchases
| Column       | Type      | Description                    |
|--------------|-----------|--------------------------------|
| id           | INTEGER   | Primary key                    |
| user_id      | INTEGER   | Buyer's Telegram ID            |
| product_id   | INTEGER   | Purchased product ID           |
| buyer_id     | TEXT      | Unique buyer ID (VS-XXXX...)   |
| amount_stars | INTEGER   | Amount paid in Stars           |
| status       | TEXT      | Purchase status                |
| created_at   | TIMESTAMP | Purchase timestamp             |

### custom_requests
| Column       | Type      | Description                    |
|--------------|-----------|--------------------------------|
| id           | INTEGER   | Primary key                    |
| user_id      | INTEGER   | Requester's Telegram ID        |
| name         | TEXT      | Client's name                  |
| username     | TEXT      | Telegram username              |
| description  | TEXT      | Task description               |
| budget       | TEXT      | Budget range                   |
| deadline     | TEXT      | Expected deadline              |
| status       | TEXT      | Request status (pending/done)  |
| created_at   | TIMESTAMP | Request timestamp              |

---

## Bot Commands

| Command    | Description                          |
|------------|--------------------------------------|
| `/start`   | Welcome message, open Mini App       |
| `/start ref_<id>` | Start with referral tracking  |
| `/help`    | Show help message                    |
| `/ref`     | Show referral link and stats         |
| `/catalog` | Browse products in chat              |
| `/top`     | Show leaderboard                     |

---

## API Endpoints

| Method | Endpoint                    | Description              |
|--------|----------------------------|--------------------------|
| GET    | `/api/health`              | Health check             |
| GET    | `/api/user/{user_id}`      | Get user data            |
| GET    | `/api/products`            | List all products        |
| GET    | `/api/leaderboard`         | Get leaderboard          |
| GET    | `/api/purchases/{user_id}` | Get user's purchases     |
| POST   | `/api/custom-request`      | Submit custom request    |

---

## Payment Flow

1. User clicks "\u041A\u0443\u043F\u0438\u0442\u044C" (Buy) on a product
2. Bot sends invoice via `send_invoice` with `currency="XTR"` (Telegram Stars)
3. User pays 120 Stars through Telegram
4. `successful_payment` handler triggers:
   - Creates purchase record with unique Buyer ID
   - Sends confirmation message with Buyer ID
   - Delivers the script file (via `file_id` or `file_path`)
   - Notifies admin of the purchase

---

## Referral System

1. User gets their unique referral link: `https://t.me/Bot?start=ref_USERID`
2. Friend clicks link and starts bot
3. Backend records `referred_by` in the friend's user record
4. Referrer's `referral_count` increments by 1
5. Both can check stats via `/ref` command or the Mini App

---

## Adding Products with Files

After uploading a file to Telegram (and getting its `file_id`):

```sql
UPDATE products
SET file_id = 'YOUR_FILE_ID_HERE'
WHERE product_key = 'automation';
```

Or insert a new product:
```sql
INSERT INTO products (product_key, name, description, price_stars, file_id)
VALUES ('new_script', 'New Script Name', 'Description here', 120, 'file_id_here');
```

---

## Multilingual Support

The system supports 3 languages:
- **Russian (ru)** — default
- **English (en)**
- **Spanish (es)**

Language detection order:
1. User's manual selection (saved in localStorage)
2. Telegram API `language_code`
3. Default to Russian

---

## Environment Variables

| Variable    | Required | Description                          |
|-------------|----------|--------------------------------------|
| BOT_TOKEN   | Yes      | Telegram Bot API token               |
| ADMIN_ID    | Yes      | Admin's Telegram ID for notifications|
| WEBAPP_URL  | Yes      | Deployed Mini App URL                |
| HOST        | No       | Server host (default: 0.0.0.0)       |
| PORT        | No       | Server port (default: 8000)          |
| WEBHOOK_URL | No       | Webhook URL for production           |

---

## Tech Stack

### Backend
- **Python 3.11+**
- **Aiogram 3.17** — Telegram Bot framework
- **FastAPI** — Web framework for TMA
- **Uvicorn** — ASGI server
- **aiosqlite** — Async SQLite
- **python-dotenv** — Environment variables

### Frontend
- **React 19 + TypeScript**
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **Lucide React** — Icons
- **Telegram WebApp JS SDK**

---

## License

MIT
