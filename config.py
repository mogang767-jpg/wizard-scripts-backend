"""
Configuration for Wizard Scripts Bot.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Telegram ID of admin for notifications
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # For production webhook mode
WEBAPP_URL = os.getenv("WEBAPP_URL", "")  # URL of the Telegram Mini App

# --- Server Configuration ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# --- Prices ---
SCRIPT_PRICE_STARS = 120  # Price in Telegram Stars

# --- Messages (Multilingual) ---
MESSAGES = {
    "ru": {
        "welcome": (
            "\U0001F680 <b>Добро пожаловать в Wizard Scripts!</b>\n\n"
            "Здесь вы можете приобрести готовые скрипты для автоматизации, "
            "парсинга и управления чатами.\n\n"
            "\U0001F4C2 <b>Каталог</b> — просмотр всех доступных скриптов\n"
            "\U0001F6D2 <b>Корзина</b> — управление покупками\n"
            "\U0001F3C6 <b>Топ</b> — таблица лидеров\n"
            "\U0001F465 <b>Рефералы</b> — приглашайте друзей\n\n"
            "Нажмите кнопку ниже, чтобы открыть магазин \U0001F447"
        ),
        "welcome_referred": (
            "\U0001F680 <b>Добро пожаловать в Wizard Scripts!</b>\n\n"
            "Вы пришли по реферальной ссылке! \U0001F389\n"
            "После вашей первой покупки пригласивший получит бонус.\n\n"
            "Нажмите кнопку ниже, чтобы открыть магазин \U0001F447"
        ),
        "purchase_success": (
            "\U0001F389 <b>Покупка успешна!</b>\n\n"
            "\U0001F4E6 <b>Товар:</b> {product_name}\n"
            "\U0001F4B0 <b>Сумма:</b> {amount} \u2B50\n"
            "\U0001F194 <b>Buyer ID:</b> <code>{buyer_id}</code>\n\n"
            "Файл отправлен выше \U0001F4E4\n\n"
            "Спасибо за покупку! \U0001F44D"
        ),
        "request_received": (
            "\U0001F4CB <b>Заявка принята!</b>\n\n"
            "Мы получили ваш запрос на индивидуальную разработку.\n"
            "Наш менеджер свяжется с вами в ближайшее время.\n\n"
            "\U0001F4AC Ожидайте сообщение от @WizardScriptsSupport"
        ),
        "help": (
            "\U0001F4AB <b>Помощь по боту</b>\n\n"
            "\U0001F4C2 <b>Каталог</b> — все доступные скрипты\n"
            "\U0001F6D2 <b>Корзина</b> — выбранные товары\n"
            "\U0001F3C6 <b>Топ</b> — рейтинг покупателей\n"
            "\U0001F465 <b>Рефералы</b> — приглашай друзей и зарабатывай\n"
            "\U0001F4CB <b>Заказ по ТЗ</b> — индивидуальная разработка\n\n"
            "\U0001F4B3 <b>Оплата:</b> Telegram Stars\n"
            "\U0001F4B0 <b>Цена каждого скрипта:</b> 120 \u2B50\n\n"
            "По вопросам: @WizardScriptsSupport"
        ),
        "admin_notification": (
            "\U0001F6A8 <b>Новая заявка!</b>\n\n"
            "\U0001F464 <b>Имя:</b> {name}\n"
            "\U0001F4AC <b>Username:</b> @{username}\n"
            "\U0001F194 <b>User ID:</b> <code>{user_id}</code>\n"
            "\U0001F4B0 <b>Бюджет:</b> {budget}\n"
            "\U0001F4C5 <b>Срок:</b> {deadline}\n\n"
            "\U0001F4DD <b>Описание:</b>\n{description}\n\n"
            "\U0001F4C6 <i>{timestamp}</i>"
        ),
        "referral_stats": (
            "\U0001F465 <b>Ваша реферальная статистика</b>\n\n"
            "Приглашено: <b>{count}</b> чел.\n"
            "Ваша ссылка:\n<code>{link}</code>"
        ),
        "product_not_found": "\u274C Товар не найден.",
        "no_file": "\u26A0\uFE0F Файл для этого скрипта пока недоступен. Обратитесь в поддержку.",
    },
    "en": {
        "welcome": (
            "\U0001F680 <b>Welcome to Wizard Scripts!</b>\n\n"
            "Here you can buy ready-made scripts for automation, "
            "parsing, and chat management.\n\n"
            "\U0001F4C2 <b>Catalog</b> — browse all available scripts\n"
            "\U0001F6D2 <b>Cart</b> — manage your purchases\n"
            "\U0001F3C6 <b>Top</b> — leaderboard\n"
            "\U0001F465 <b>Referrals</b> — invite friends\n\n"
            "Click the button below to open the store \U0001F447"
        ),
        "welcome_referred": (
            "\U0001F680 <b>Welcome to Wizard Scripts!</b>\n\n"
            "You came via a referral link! \U0001F389\n"
            "After your first purchase, the referrer will receive a bonus.\n\n"
            "Click the button below to open the store \U0001F447"
        ),
        "purchase_success": (
            "\U0001F389 <b>Purchase successful!</b>\n\n"
            "\U0001F4E6 <b>Product:</b> {product_name}\n"
            "\U0001F4B0 <b>Amount:</b> {amount} \u2B50\n"
            "\U0001F194 <b>Buyer ID:</b> <code>{buyer_id}</code>\n\n"
            "File sent above \U0001F4E4\n\n"
            "Thank you for your purchase! \U0001F44D"
        ),
        "request_received": (
            "\U0001F4CB <b>Request received!</b>\n\n"
            "We have received your custom development request.\n"
            "Our manager will contact you shortly.\n\n"
            "\U0001F4AC Expect a message from @WizardScriptsSupport"
        ),
        "help": (
            "\U0001F4AB <b>Bot Help</b>\n\n"
            "\U0001F4C2 <b>Catalog</b> — all available scripts\n"
            "\U0001F6D2 <b>Cart</b> — selected items\n"
            "\U0001F3C6 <b>Top</b> — buyer rankings\n"
            "\U0001F465 <b>Referrals</b> — invite friends and earn\n"
            "\U0001F4CB <b>Custom Order</b> — individual development\n\n"
            "\U0001F4B3 <b>Payment:</b> Telegram Stars\n"
            "\U0001F4B0 <b>Price per script:</b> 120 \u2B50\n\n"
            "Support: @WizardScriptsSupport"
        ),
        "admin_notification": (
            "\U0001F6A8 <b>New Request!</b>\n\n"
            "\U0001F464 <b>Name:</b> {name}\n"
            "\U0001F4AC <b>Username:</b> @{username}\n"
            "\U0001F194 <b>User ID:</b> <code>{user_id}</code>\n"
            "\U0001F4B0 <b>Budget:</b> {budget}\n"
            "\U0001F4C5 <b>Deadline:</b> {deadline}\n\n"
            "\U0001F4DD <b>Description:</b>\n{description}\n\n"
            "\U0001F4C6 <i>{timestamp}</i>"
        ),
        "referral_stats": (
            "\U0001F465 <b>Your Referral Stats</b>\n\n"
            "Invited: <b>{count}</b> people\n"
            "Your link:\n<code>{link}</code>"
        ),
        "product_not_found": "\u274C Product not found.",
        "no_file": "\u26A0\uFE0F File for this script is currently unavailable. Contact support.",
    },
    "es": {
        "welcome": (
            "\U0001F680 <b>\u00A1Bienvenido a Wizard Scripts!</b>\n\n"
            "Aqu\u00ED puedes comprar scripts listos para automatizaci\u00F3n, "
            "parsing y gesti\u00F3n de chats.\n\n"
            "\U0001F4C2 <b>Cat\u00E1logo</b> — todos los scripts disponibles\n"
            "\U0001F6D2 <b>Carrito</b> — gestiona tus compras\n"
            "\U0001F3C6 <b>Top</b> — tabla de clasificaci\u00F3n\n"
            "\U0001F465 <b>Referidos</b> — invita amigos\n\n"
            "Haz clic en el bot\u00F3n para abrir la tienda \U0001F447"
        ),
        "welcome_referred": (
            "\U0001F680 <b>\u00A1Bienvenido a Wizard Scripts!</b>\n\n"
            "\u00A1Viniste por un enlace de referido! \U0001F389\n"
            "Despu\u00E9s de tu primera compra, el referente recibir\u00E1 una bonificaci\u00F3n.\n\n"
            "Haz clic en el bot\u00F3n para abrir la tienda \U0001F447"
        ),
        "purchase_success": (
            "\U0001F389 <b>\u00A1Compra exitosa!</b>\n\n"
            "\U0001F4E6 <b>Producto:</b> {product_name}\n"
            "\U0001F4B0 <b>Cantidad:</b> {amount} \u2B50\n"
            "\U0001F194 <b>Buyer ID:</b> <code>{buyer_id}</code>\n\n"
            "Archivo enviado arriba \U0001F4E4\n\n"
            "\u00A1Gracias por tu compra! \U0001F44D"
        ),
        "request_received": (
            "\U0001F4CB <b>\u00A1Solicitud recibida!</b>\n\n"
            "Hemos recibido tu solicitud de desarrollo personalizado.\n"
            "Nuestro gerente se pondr\u00E1 en contacto contigo pronto.\n\n"
            "\U0001F4AC Espera un mensaje de @WizardScriptsSupport"
        ),
        "help": (
            "\U0001F4AB <b>Ayuda del Bot</b>\n\n"
            "\U0001F4C2 <b>Cat\u00E1logo</b> — todos los scripts\n"
            "\U0001F6D2 <b>Carrito</b> — art\u00EDculos seleccionados\n"
            "\U0001F3C6 <b>Top</b> — clasificaci\u00F3n de compradores\n"
            "\U0001F465 <b>Referidos</b> — invita amigos y gana\n"
            "\U0001F4CB <b>Pedido personalizado</b> — desarrollo individual\n\n"
            "\U0001F4B3 <b>Pago:</b> Telegram Stars\n"
            "\U0001F4B0 <b>Precio por script:</b> 120 \u2B50\n\n"
            "Soporte: @WizardScriptsSupport"
        ),
        "admin_notification": (
            "\U0001F6A8 <b>\u00A1Nueva solicitud!</b>\n\n"
            "\U0001F464 <b>Nombre:</b> {name}\n"
            "\U0001F4AC <b>Username:</b> @{username}\n"
            "\U0001F194 <b>User ID:</b> <code>{user_id}</code>\n"
            "\U0001F4B0 <b>Presupuesto:</b> {budget}\n"
            "\U0001F4C5 <b>Plazo:</b> {deadline}\n\n"
            "\U0001F4DD <b>Descripci\u00F3n:</b>\n{description}\n\n"
            "\U0001F4C6 <i>{timestamp}</i>"
        ),
        "referral_stats": (
            "\U0001F465 <b>Tus estad\u00EDsticas de referido</b>\n\n"
            "Invitados: <b>{count}</b> personas\n"
            "Tu enlace:\n<code>{link}</code>"
        ),
        "product_not_found": "\u274C Producto no encontrado.",
        "no_file": "\u26A0\uFE0F El archivo para este script no est\u00E1 disponible. Contacta soporte.",
    },
}


def get_message(lang: str, key: str) -> str:
    """Get a localized message."""
    lang_messages = MESSAGES.get(lang, MESSAGES["ru"])
    return lang_messages.get(key, MESSAGES["ru"].get(key, key))
