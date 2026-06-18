"""
Wizard Scripts Telegram Bot (Aiogram 3.x)

Handles:
- /start command with referral tracking
- Product catalog and purchases
- Telegram Stars payment processing
- File delivery after successful payment
- Admin notifications for custom requests
- /help and /ref commands
"""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    SuccessfulPayment,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    LabeledPrice,
    ShippingOption,
)
from aiogram.exceptions import TelegramAPIError

from config import (
    BOT_TOKEN,
    ADMIN_ID,
    WEBAPP_URL,
    SCRIPT_PRICE_STARS,
    get_message,
)
from database import (
    init_db,
    get_or_create_user,
    get_user,
    get_products,
    get_product,
    get_product_by_key,
    create_purchase,
    get_referral_count,
    create_custom_request,
    get_leaderboard,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Initialize Bot & Dispatcher ---
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()

# --- Helper Functions ---

def get_user_lang(message: Message) -> str:
    """Extract user's language code, default to 'ru'."""
    if message.from_user and message.from_user.language_code:
        code = message.from_user.language_code.lower()
        if code.startswith("es"):
            return "es"
        elif code.startswith("en"):
            return "en"
    return "ru"


def build_webapp_button(user_id: int, lang: str) -> InlineKeyboardMarkup:
    """Build the main webapp open button."""
    webapp_url = f"{WEBAPP_URL}?user_id={user_id}" if WEBAPP_URL else ""
    button_text = {
        "ru": "\U0001F4C2 Открыть магазин",
        "en": "\U0001F4C2 Open Store",
        "es": "\U0001F4C2 Abrir tienda",
    }.get(lang, "\U0001F4C2 Open Store")

    if webapp_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=button_text,
                        web_app=WebAppInfo(url=webapp_url),
                    )
                ]
            ]
        )
    # Fallback without webapp
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data="catalog",
                )
            ]
        ]
    )


def build_catalog_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for product catalog."""
    texts = {
        "ru": {"buy": "\U0001F4B3 Купить за 120\u2B50", "back": "\U0001F519 Назад"},
        "en": {"buy": "\U0001F4B3 Buy for 120\u2B50", "back": "\U0001F519 Back"},
        "es": {"buy": "\U0001F4B3 Comprar por 120\u2B50", "back": "\U0001F519 Atr\u00E1s"},
    }.get(lang, {"buy": "\U0001F4B3 Buy for 120\u2B50", "back": "\U0001F519 Back"})

    buttons = [
        [
            InlineKeyboardButton(
                text=texts["buy"],
                callback_data="buy_script",
            )
        ],
        [
            InlineKeyboardButton(
                text=texts["back"],
                callback_data="back_to_main",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Command Handlers ---

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command with optional referral parameter."""
    if not message.from_user:
        return

    user = message.from_user
    lang = get_user_lang(message)

    # Parse referral
    referred_by = None
    if message.text and len(message.text.split()) > 1:
        payload = message.text.split(maxsplit=1)[1]
        if payload.startswith("ref_"):
            try:
                referred_by = int(payload.split("_")[1])
            except (ValueError, IndexError):
                pass

    # Create or update user
    await get_or_create_user(
        tg_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        referred_by=referred_by if referred_by != user.id else None,
    )

    # Send welcome message
    if referred_by and referred_by != user.id:
        welcome_text = get_message(lang, "welcome_referred")
    else:
        welcome_text = get_message(lang, "welcome")

    await message.answer(
        welcome_text,
        reply_markup=build_webapp_button(user.id, lang),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    lang = get_user_lang(message)
    help_text = get_message(lang, "help")
    await message.answer(help_text)


@router.message(Command("ref"))
async def cmd_ref(message: Message) -> None:
    """Handle /ref command to show referral info."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    lang = get_user_lang(message)
    count = await get_referral_count(user_id)

    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    text = get_message(lang, "referral_stats").format(count=count, link=link)
    await message.answer(text)


@router.message(Command("catalog"))
async def cmd_catalog(message: Message) -> None:
    """Handle /catalog command."""
    if not message.from_user:
        return

    lang = get_user_lang(message)
    products = await get_products()

    if not products:
        await message.answer(get_message(lang, "product_not_found"))
        return

    # Send each product as a card
    for product in products:
        text = (
            f"<b>{product['name']}</b>\n"
            f"{product['description']}\n\n"
            f"\U0001F4B0 <b>Цена:</b> {product['price_stars']}\u2B50"
        )
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"\U0001F4B3 Купить ({product['price_stars']}\u2B50)",
                            callback_data=f"buy_{product['id']}",
                        )
                    ]
                ]
            ),
        )


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    """Handle /top command for leaderboard."""
    lang = get_user_lang(message)
    leaders = await get_leaderboard(10)

    if not leaders:
        await message.answer("\U0001F3C6 Пока нет данных / No data yet.")
        return

    text = "\U0001F3C6 <b>Топ покупателей</b>\n\n"
    medals = ["\U0001F947", "\U0001F948", "\U0001F949"]

    for i, leader in enumerate(leaders):
        medal = medals[i] if i < 3 else f"{i + 1}."
        name = leader["username"] or leader["first_name"] or "Anonymous"
        text += f"{medal} {name} — {leader['purchases']} пок. ({leader['spent']}\u2B50)\n"

    await message.answer(text)


# --- Callback Handlers ---

@router.callback_query(F.data == "catalog")
async def callback_catalog(callback: CallbackQuery) -> None:
    """Handle catalog callback."""
    if not callback.message:
        return
    lang = get_user_lang(callback.message)
    await cmd_catalog(callback.message)
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def callback_back(callback: CallbackQuery) -> None:
    """Handle back to main callback."""
    if not callback.message or not callback.from_user:
        return
    lang = get_user_lang(callback.message)
    welcome_text = get_message(lang, "welcome")
    await callback.message.edit_text(
        welcome_text,
        reply_markup=build_webapp_button(callback.from_user.id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def callback_buy(callback: CallbackQuery) -> None:
    """Handle buy button - initiate payment."""
    if not callback.message or not callback.from_user:
        await callback.answer("Error")
        return

    product_id_str = callback.data.split("_")[1]  # type: ignore
    try:
        product_id = int(product_id_str)
    except ValueError:
        await callback.answer("Invalid product")
        return

    product = await get_product(product_id)
    if not product:
        lang = get_user_lang(callback.message)
        await callback.answer(get_message(lang, "product_not_found"))
        return

    # Send invoice for Telegram Stars payment
    prices = [LabeledPrice(label=product["name"], amount=product["price_stars"])]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=product["name"],
        description=product["description"],
        payload=f"product_{product['id']}",
        provider_token="",  # Empty for Telegram Stars
        currency="XTR",  # Telegram Stars currency code
        prices=prices,
        start_parameter=f"buy_{product['id']}",
    )
    await callback.answer()


# --- Payment Handlers ---

@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery) -> None:
    """Handle pre-checkout query - always approve."""
    await bot.answer_pre_checkout_query(query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    """Handle successful payment - deliver file and send confirmation."""
    if not message.from_user or not message.successful_payment:
        return

    payment: SuccessfulPayment = message.successful_payment
    user_id = message.from_user.id
    lang = get_user_lang(message)

    # Extract product ID from payload
    payload = payment.invoice_payload
    if not payload.startswith("product_"):
        logger.warning(f"Unknown payment payload: {payload}")
        return

    try:
        product_id = int(payload.split("_")[1])
    except (ValueError, IndexError):
        logger.warning(f"Invalid payment payload: {payload}")
        return

    product = await get_product(product_id)
    if not product:
        await message.answer(get_message(lang, "product_not_found"))
        return

    # Create purchase record
    buyer_id = await create_purchase(
        user_id=user_id,
        product_id=product_id,
        amount_stars=payment.total_amount,
    )

    # Send success message with buyer ID
    success_text = get_message(lang, "purchase_success").format(
        product_name=product["name"],
        amount=payment.total_amount,
        buyer_id=buyer_id,
    )

    await message.answer(success_text)

    # Deliver file if available
    if product.get("file_id"):
        try:
            await bot.send_document(
                chat_id=user_id,
                document=product["file_id"],
                caption=f"\U0001F4E5 <b>{product['name']}</b>\nBuyer ID: <code>{buyer_id}</code>",
            )
        except TelegramAPIError as e:
            logger.error(f"Failed to send file: {e}")
            await message.answer(get_message(lang, "no_file"))
    elif product.get("file_path"):
        try:
            await bot.send_document(
                chat_id=user_id,
                document=product["file_path"],  # type: ignore
                caption=f"\U0001F4E5 <b>{product['name']}</b>\nBuyer ID: <code>{buyer_id}</code>",
            )
        except TelegramAPIError as e:
            logger.error(f"Failed to send file: {e}")
            await message.answer(get_message(lang, "no_file"))
    else:
        await message.answer(get_message(lang, "no_file"))

    # Notify admin
    if ADMIN_ID:
        try:
            admin_text = (
                f"\U0001F4B0 <b>New Purchase!</b>\n\n"
                f"\U0001F464 User: {message.from_user.username or message.from_user.first_name}\n"
                f"\U0001F194 User ID: <code>{user_id}</code>\n"
                f"\U0001F4E6 Product: {product['name']}\n"
                f"\U0001F4B0 Amount: {payment.total_amount}\u2B50\n"
                f"\U0001F194 Buyer ID: <code>{buyer_id}</code>\n"
                f"\U0001F4C6 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await bot.send_message(ADMIN_ID, admin_text)
        except TelegramAPIError as e:
            logger.error(f"Failed to notify admin: {e}")


# --- Error Handler ---

@router.error()
async def error_handler(event) -> None:
    """Handle errors."""
    logger.error(f"Update processing error: {event}")


# --- Main Entry Point ---

async def main() -> None:
    """Start the bot."""
    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Register router
    dp.include_router(router)

    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
