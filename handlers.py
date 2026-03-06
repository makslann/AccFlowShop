"""Command and callback handlers for AccFlow Shop bot."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from database import (
    create_order,
    ensure_user,
    get_product,
    get_products_by_category,
    get_user_orders,
)
from keyboards import (
    CB_BACK,
    CB_CATEGORY,
    CB_MAIN_BUY,
    CB_MAIN_DEALS,
    CB_MAIN_EARN,
    CB_MAIN_FAQ,
    CB_MAIN_REFERRAL,
    CB_MAIN_SUPPORT,
    CB_ORDER,
    CB_PRODUCT,
    categories_keyboard,
    main_inline_keyboard,
    product_actions,
    products_keyboard,
)

router = Router(name=__name__)

SHOP_NAME = "AccFlow Shop"
SUPPORT_LINK = "https://t.me/AccFlow_Support"


WELCOME_MESSAGE = (
    "<b>Добро пожаловать в AccFlow Shop — автоматизированный сервис по поставке бизнес-аккаунтов Stripe! 💳🚀</b>\n\n"
    "Мы предлагаем качественные решения для приема платежей в ваших проектах. Каждый аккаунт проходит многоэтапную проверку перед продажей, что гарантирует высокую стабильность работы и долговечность. ✅\n\n"
    "Почему выбирают нас:\n"
    "⏳ Гарантированная отлежка: Мы не продаем «свежерегов». Все аккаунты имеют историю и необходимую выдержку.\n"
    "⚡️ Мгновенная выдача: Данные приходят в чат автоматически сразу после подтверждения оплаты.\n"
    "👨‍💻 Поддержка 24/7: Помогаем с вопросами запуска, эксплуатации и прохождения проверок.\n"
    "🛡 Безопасная оплата: Принимаем платежи через официальный сервис Telegram — Crypto Bot.\n\n"
    "<b>Для ознакомления с ассортиментом и актуальным наличием используйте меню ниже 👇</b>\n\n"
    "🆘 Техническая поддержка: @AccFlow_Support"
)


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    """Welcome and main menu."""
    ensure_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=main_inline_keyboard(),
        parse_mode="HTML",
    )


# --- Main menu callbacks (buttons in welcome message) ---


@router.callback_query(F.data == CB_MAIN_BUY)
async def main_buy(callback: CallbackQuery) -> None:
    """Show category selection (Amazon, eBay)."""
    await callback.message.answer(
        "Выберите категорию:",
        reply_markup=categories_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == CB_MAIN_SUPPORT)
async def main_support(callback: CallbackQuery) -> None:
    """Support link."""
    await callback.message.answer(
        f"🆘 <b>Поддержка</b>\n\nПо всем вопросам: {SUPPORT_LINK}",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == CB_MAIN_FAQ)
async def main_faq(callback: CallbackQuery) -> None:
    """FAQ section."""
    text = (
        "❓ <b>Часто задаваемые вопросы</b>\n\n"
        "Здесь будет раздел с ответами на популярные вопросы. "
        "Пока по любым вопросам пишите в поддержку: @AccFlow_Support"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == CB_MAIN_DEALS)
async def main_deals(callback: CallbackQuery) -> None:
    """Successful deals / reviews."""
    text = (
        "✅ <b>Успешные сделки</b>\n\n"
        "Раздел с отзывами и статистикой успешных сделок. "
        "Скоро здесь появятся реальные кейсы наших клиентов."
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == CB_MAIN_REFERRAL)
async def main_referral(callback: CallbackQuery) -> None:
    """Referral program."""
    text = (
        "👥 <b>Реферальная система</b>\n\n"
        "Приглашайте друзей и получайте бонусы с их покупок. "
        "Детали и ваша реферальная ссылка — скоро в этом разделе."
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == CB_MAIN_EARN)
async def main_earn(callback: CallbackQuery) -> None:
    """Earn section."""
    text = (
        "💰 <b>Заработать</b>\n\n"
        "Способы заработка с AccFlow Shop: партнёрство, рефералы, промо. "
        "Подробности у поддержки: @AccFlow_Support"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith(CB_CATEGORY))
async def category_selected(callback: CallbackQuery) -> None:
    """Show products for selected category."""
    slug = callback.data.removeprefix(CB_CATEGORY)
    products = get_products_by_category(slug)
    category_name = "Amazon" if slug == "amazon" else "eBay"

    if not products:
        await callback.message.edit_text(
            f"В категории **{category_name}** пока нет товаров.",
            reply_markup=categories_keyboard(),
            parse_mode="Markdown",
        )
    else:
        await callback.message.edit_text(
            f"📦 **{category_name}** — выберите товар:",
            reply_markup=products_keyboard(slug, products),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith(CB_PRODUCT))
async def product_selected(callback: CallbackQuery) -> None:
    """Show product details and buy button."""
    product_id = int(callback.data.removeprefix(CB_PRODUCT))
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    text = (
        f"**{product['name']}**\n\n"
        f"{product['description'] or '—'}\n\n"
        f"💰 Цена: **{product['price']:.0f} ₽**"
    )
    await callback.message.edit_text(
        text,
        reply_markup=product_actions(product_id),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith(CB_BACK))
async def back_pressed(callback: CallbackQuery) -> None:
    """Back to categories."""
    if "categories" in callback.data:
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=categories_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith(CB_ORDER))
async def order_placed(callback: CallbackQuery) -> None:
    """Create order and confirm."""
    product_id = int(callback.data.removeprefix(CB_ORDER))
    product = get_product(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    ensure_user(
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.first_name,
    )
    order_id = create_order(callback.from_user.id, product_id)

    await callback.message.edit_text(
        f"✅ **Заказ #{order_id} оформлен**\n\n"
        f"Товар: {product['name']}\n"
        f"Сумма: {product['price']:.0f} ₽\n\n"
        "С вами свяжется поддержка для завершения оплаты.",
        reply_markup=categories_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer("Заказ оформлен!")
