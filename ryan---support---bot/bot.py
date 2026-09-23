from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8969324995:AAHaPgGfaoM2ewEZmvAZYpAwzZlkcPltRpc"
ADMIN_ID = 8877797203


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("🚛 Bobtail", callback_data="bobtail")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        [InlineKeyboardButton("⚠️ Reject Under Planning Error", callback_data="planning_error")],
        [InlineKeyboardButton("⏰ On Time to Origin", callback_data="origin")],
        [InlineKeyboardButton("🏁 On Time to Destination", callback_data="destination")],
        [InlineKeyboardButton("🗑️ Remove", callback_data="remove")],
        [InlineKeyboardButton("📞 Broker Contact for Sale", callback_data="broker")],
    ]

    await update.message.reply_text(
        "🚛 RYAN SUPPORT\n\n"
        "Welcome! 👋\n\n"
        "Select the issue you need help with:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data in ["bobtail", "cancel", "planning_error"]:

        context.user_data["step"] = "photo"
        context.user_data["issue"] = query.data

        await query.message.reply_text(
            "📸 Please send us a clear photo showing the overall "
            "situation with the load/trailer."
        )

    elif query.data in ["origin", "destination"]:

        if query.data == "origin":
            context.user_data["scorecard_type"] = "On Time to Origin"
        else:
            context.user_data["scorecard_type"] = "On Time to Destination"

        context.user_data["step"] = "number"

        await query.message.reply_text(
            f"📊 {context.user_data['scorecard_type']}\n\n"
            "How many loads need to be removed from the scorecard?"
        )

    elif query.data == "remove":

        await query.message.reply_text(
            "🚧 Remove is currently unavailable.\n\n"
            "Please check back later."
        )

    elif query.data == "broker":

        context.user_data["step"] = "telegram"

        await query.message.reply_text(
            "📞 Broker Contact for Sale\n\n"
            "Please enter your Telegram username:"
        )


async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("step") != "photo":
        return

    if not update.message.photo:
        await update.message.reply_text("Please send a photo.")
        return

    issue = context.user_data.get("issue")

    issue_names = {
        "bobtail": "🚛 Bobtail",
        "cancel": "❌ Cancel",
        "planning_error": "⚠️ Reject Under Planning Error",
    }

    issue_name = issue_names.get(issue, "Support Request")

    user = update.effective_user

    admin_message = (
        "🚨 NEW SUPPORT REQUEST\n\n"
        f"📌 Issue: {issue_name}\n"
        f"👤 User: {user.first_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"📱 Username: @{user.username if user.username else 'No username'}\n\n"
        "📸 Photo attached below."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📌 {issue_name}"
    )

    context.user_data["step"] = None

    await update.message.reply_text(
        "✅ Photo received.\n\n"
        "Our support team will review your request and contact you shortly.\n\n"
        "Please keep your Telegram available."
    )


async def message_received(update: Update, context: ContextTypes.DEFAULT_TYPE):

    step = context.user_data.get("step")

    if not step:
        return

    text = update.message.text.strip()
    user = update.effective_user

    if step == "number":

        if not text.isdigit() or int(text) <= 0:
            await update.message.reply_text(
                "Please enter a valid number.\n\n"
                "For example: 1, 2, 3..."
            )
            return

        context.user_data["load_count"] = int(text)
        context.user_data["step"] = "scac"

        await update.message.reply_text(
            "🏷️ Please enter your Company SCAC Code:"
        )

    elif step == "scac":

        context.user_data["scac"] = text.upper()
        context.user_data["step"] = "company"

        await update.message.reply_text(
            "🏢 Please enter your Company Name:"
        )

    elif step == "company":

        context.user_data["company"] = text
        context.user_data["step"] = "phone"

        await update.message.reply_text(
            "📞 Please enter a Contact Phone Number:"
        )

    elif step == "phone":

        context.user_data["phone"] = text
        context.user_data["step"] = None

        scorecard_type = context.user_data["scorecard_type"]
        load_count = context.user_data["load_count"]
        scac = context.user_data["scac"]
        company = context.user_data["company"]
        phone = context.user_data["phone"]

        admin_message = (
            "🚨 NEW SUPPORT REQUEST\n\n"
            f"📌 Issue: {scorecard_type}\n"
            f"📦 Loads: {load_count}\n"
            f"🏷️ SCAC: {scac}\n"
            f"🏢 Company: {company}\n"
            f"📞 Contact: {phone}\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"📱 Username: @{user.username if user.username else 'No username'}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message
        )

        await update.message.reply_text(
            "✅ Information received!\n\n"
            "Our support team will review your request "
            "and contact you shortly.\n\n"
            "Please keep your phone available."
        )

    elif step == "telegram":

        context.user_data["telegram"] = text
        context.user_data["step"] = "price"

        await update.message.reply_text(
            "💰 Please enter your estimated price:"
        )

    elif step == "price":

        context.user_data["price"] = text
        context.user_data["step"] = None

        telegram_username = context.user_data["telegram"]
        price = context.user_data["price"]

        admin_message = (
            "🚨 NEW BROKER SALE REQUEST\n\n"
            f"📞 Telegram: {telegram_username}\n"
            f"💰 Estimated Price: {price}\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"📱 Username: @{user.username if user.username else 'No username'}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message
        )

        await update.message.reply_text(
            "✅ Information received!\n\n"
            "Our support team will review your request "
            "and contact you shortly on Telegram.\n\n"
            "Please keep your Telegram available."
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.add_handler(
        MessageHandler(filters.PHOTO, photo_received)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_received
        )
    )

    print("🚛 Ryan Support Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()
