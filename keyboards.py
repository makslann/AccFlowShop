"""Keyboards for AccFlow Shop bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data for main inline menu
CB_MAIN_BUY = "main:buy"
CB_MAIN_SUPPORT = "main:support"
CB_MAIN_FAQ = "main:faq"
CB_MAIN_DEALS = "main:deals"
CB_MAIN_REFERRAL = "main:referral"
CB_MAIN_EARN = "main:earn"

# Callback data prefixes
CB_CATEGORY = "cat:"
CB_PRODUCT = "prod:"
CB_BACK = "back:"
CB_ORDER = "order:"


def main_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons in welcome message: Buy, Support, FAQ, Deals, Referral, Earn."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data=CB_MAIN_BUY)],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data=CB_MAIN_SUPPORT),
            InlineKeyboardButton(text="❓ FAQ", callback_data=CB_MAIN_FAQ),
        ],
        [
            InlineKeyboardButton(text="✅ Успешные сделки", callback_data=CB_MAIN_DEALS),
            InlineKeyboardButton(text="👥 Реферальная система", callback_data=CB_MAIN_REFERRAL),
        ],
        [InlineKeyboardButton(text="💰 Заработать", callback_data=CB_MAIN_EARN)],
    ])


def categories_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard: Amazon, eBay."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Amazon", callback_data=f"{CB_CATEGORY}amazon")],
        [InlineKeyboardButton(text="eBay", callback_data=f"{CB_CATEGORY}ebay")],
    ])


def back_to_categories() -> InlineKeyboardMarkup:
    """Back button to categories."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к категориям", callback_data=f"{CB_BACK}categories")],
    ])


def products_keyboard(category_slug: str, products: list[dict]) -> InlineKeyboardMarkup:
    """Inline keyboard with product list and back button."""
    buttons = [
        [InlineKeyboardButton(
            text=f"{p['name']} — {p['price']:.0f} ₽",
            callback_data=f"{CB_PRODUCT}{p['id']}",
        )]
        for p in products
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад к категориям", callback_data=f"{CB_BACK}categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_actions(product_id: int) -> InlineKeyboardMarkup:
    """Buy and back buttons for product view."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Купить", callback_data=f"{CB_ORDER}{product_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"{CB_BACK}categories")],
    ])
