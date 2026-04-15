from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)
from supabase import create_client, Client

import config
import strings

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

ASK_AMOUNT, ASK_DESCRIPTION = range(2)


def get_username(update: Update) -> str:
    user = update.effective_user
    return user.username or user.first_name


def is_allowed(user_id: int) -> bool:
    if user_id == config.ADMIN_ID:
        return True
    result = supabase.table("allowed_users").select("telegram_id").eq("telegram_id", user_id).execute()
    return len(result.data) > 0


async def check_access(update: Update) -> bool:
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text(strings.NO_ACCESS)
        return False
    return True


def category_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(label, callback_data=f"cat:{value}")
        for label, value in config.CATEGORIES
    ]
    rows = [buttons[:3], buttons[3:]]
    return InlineKeyboardMarkup(rows)


# --- Conversation flow: /add ---

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return ConversationHandler.END
    args = context.args

    # One-liner: /add 50 supermercado [@username]
    if args and len(args) >= 2:
        try:
            amount = float(args[0].replace(",", "."))
        except ValueError:
            await update.message.reply_text(strings.ADD_INVALID_AMOUNT)
            return ConversationHandler.END

        if amount <= 0:
            await update.message.reply_text(strings.ADD_ZERO_AMOUNT)
            return ConversationHandler.END

        if args[-1].startswith("@"):
            paid_by = args[-1][1:]
            description = " ".join(args[1:-1])
        else:
            paid_by = get_username(update)
            description = " ".join(args[1:])

        if not description:
            await update.message.reply_text(strings.ADD_NO_DESCRIPTION)
            return ConversationHandler.END

        context.user_data["pending"] = {
            "amount": amount,
            "description": description,
            "paid_by": paid_by,
        }

        await update.message.reply_text(
            f"*{config.CURRENCY}{amount:.2f} — {description}*\n{strings.SELECT_CATEGORY}",
            parse_mode="Markdown",
            reply_markup=category_keyboard(),
        )
        return ConversationHandler.END

    # Conversation flow: /add with no args
    await update.message.reply_text(strings.ASK_AMOUNT)
    return ASK_AMOUNT


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        amount = float(text.replace(",", "."))
    except ValueError:
        await update.message.reply_text(strings.ASK_AMOUNT_INVALID)
        return ASK_AMOUNT

    if amount <= 0:
        await update.message.reply_text(strings.ASK_AMOUNT_ZERO)
        return ASK_AMOUNT

    context.user_data["pending"] = {"amount": amount}
    await update.message.reply_text(strings.ASK_DESCRIPTION, parse_mode="Markdown")
    return ASK_DESCRIPTION


async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split()

    if parts and parts[-1].startswith("@"):
        paid_by = parts[-1][1:]
        description = " ".join(parts[:-1])
    else:
        paid_by = get_username(update)
        description = " ".join(parts)

    if not description:
        await update.message.reply_text(strings.ASK_DESCRIPTION_EMPTY, parse_mode="Markdown")
        return ASK_DESCRIPTION

    context.user_data["pending"].update({
        "description": description,
        "paid_by": paid_by,
    })

    amount = context.user_data["pending"]["amount"]
    await update.message.reply_text(
        f"*{config.CURRENCY}{amount:.2f} — {description}*\n{strings.SELECT_CATEGORY}",
        parse_mode="Markdown",
        reply_markup=category_keyboard(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("pending", None)
    await update.message.reply_text(strings.CANCELLED)
    return ConversationHandler.END


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("pending", None)
    await update.effective_message.reply_text(strings.TIMEOUT)
    return ConversationHandler.END


# --- Category callback ---

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_allowed(update.effective_user.id):
        await query.edit_message_text(strings.NO_ACCESS)
        return

    category = query.data.split(":")[1]
    pending = context.user_data.get("pending")

    if not pending:
        await query.edit_message_text(strings.CATEGORY_ERROR)
        return

    now = datetime.now()
    supabase.table("expenses").insert({
        "amount": pending["amount"],
        "description": pending["description"],
        "paid_by": pending["paid_by"],
        "category": category,
        "month": now.month,
        "year": now.year,
    }).execute()

    context.user_data.pop("pending", None)

    category_label = next(label for label, value in config.CATEGORIES if value == category)
    await query.edit_message_text(
        f"✅ {config.CURRENCY}{pending['amount']:.2f} — {pending['description']} · @{pending['paid_by']} · {category_label}"
    )


# --- Other commands ---

async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    now = datetime.now()
    result = (
        supabase.table("expenses")
        .select("*")
        .eq("month", now.month)
        .eq("year", now.year)
        .order("created_at")
        .execute()
    )

    if not result.data:
        await update.message.reply_text(strings.NO_EXPENSES)
        return

    month_name = now.strftime("%B %Y")
    lines = [f"📋 *Gastos {month_name}*\n"]
    for e in result.data:
        cat = f" · {e['category']}" if e.get("category") else ""
        lines.append(f"• {config.CURRENCY}{e['amount']:.2f} — {e['description']} · @{e['paid_by']}{cat}")

    await update.message.reply_text("\n".join(lines))


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    now = datetime.now()
    result = (
        supabase.table("expenses")
        .select("amount")
        .eq("month", now.month)
        .eq("year", now.year)
        .execute()
    )

    total_amount = sum(e["amount"] for e in result.data)
    month_name = now.strftime("%B %Y")
    await update.message.reply_text(
        f"💰 Total *{month_name}*: {config.CURRENCY}{total_amount:.2f}",
        parse_mode="Markdown"
    )


async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    user = get_username(update)
    now = datetime.now()
    result = (
        supabase.table("expenses")
        .select("*")
        .eq("month", now.month)
        .eq("year", now.year)
        .eq("paid_by", user)
        .order("created_at")
        .execute()
    )

    if not result.data:
        await update.message.reply_text(strings.NO_MY_EXPENSES)
        return

    total_amount = sum(e["amount"] for e in result.data)
    month_name = now.strftime("%B %Y")
    lines = [f"👤 *Mis gastos {month_name}*\n"]
    for e in result.data:
        cat = f" · {e['category']}" if e.get("category") else ""
        lines.append(f"• {config.CURRENCY}{e['amount']:.2f} — {e['description']}{cat}")
    lines.append(f"\nTotal: *{config.CURRENCY}{total_amount:.2f}*")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    now = datetime.now()
    result = (
        supabase.table("expenses")
        .select("*")
        .eq("month", now.month)
        .eq("year", now.year)
        .execute()
    )

    if not result.data:
        await update.message.reply_text(strings.NO_EXPENSES)
        return

    totals: dict[str, float] = {}
    for e in result.data:
        paid_by = e["paid_by"]
        totals[paid_by] = totals.get(paid_by, 0) + e["amount"]

    grand_total = sum(totals.values())
    month_name = now.strftime("%B %Y")
    lines = [f"📊 *{month_name} — Total: {config.CURRENCY}{grand_total:.2f}*\n"]
    for user, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"@{user} → {config.CURRENCY}{amount:.2f}")

    await update.message.reply_text("\n".join(lines))


async def categories_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    now = datetime.now()
    result = (
        supabase.table("expenses")
        .select("amount, category")
        .eq("month", now.month)
        .eq("year", now.year)
        .execute()
    )

    if not result.data:
        await update.message.reply_text(strings.NO_EXPENSES)
        return

    totals: dict[str, float] = {}
    for e in result.data:
        cat = e.get("category") or "other"
        totals[cat] = totals.get(cat, 0) + e["amount"]

    cat_labels = {value: label for label, value in config.CATEGORIES}
    month_name = now.strftime("%B %Y")
    lines = [f"📊 *{month_name} by category*\n"]
    for cat, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        label = cat_labels.get(cat, cat)
        lines.append(f"{label} → {config.CURRENCY}{amount:.2f}")

    await update.message.reply_text("\n".join(lines))


async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text(strings.ADMIN_ONLY_ADD)
        return

    args = context.args
    if not args or not args[0].startswith("@"):
        await update.message.reply_text(strings.ADDUSER_USAGE)
        return

    if len(args) < 2:
        await update.message.reply_text(strings.ADDUSER_MISSING_ID)
        return

    username = args[0][1:]
    try:
        telegram_id = int(args[1])
    except ValueError:
        await update.message.reply_text(strings.ADDUSER_INVALID_ID)
        return

    supabase.table("allowed_users").upsert({
        "telegram_id": telegram_id,
        "username": username,
    }).execute()

    await update.message.reply_text(strings.ADDUSER_SUCCESS.format(username=username))


async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text(strings.ADMIN_ONLY_REMOVE)
        return

    args = context.args
    if not args or not args[0].startswith("@"):
        await update.message.reply_text(strings.REMOVEUSER_USAGE)
        return

    username = args[0][1:]
    supabase.table("allowed_users").delete().eq("username", username).execute()
    await update.message.reply_text(strings.REMOVEUSER_SUCCESS.format(username=username))


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await update.message.reply_text(strings.HELP_TEXT, parse_mode="Markdown")


def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount)],
            ASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=60,
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(category_callback, pattern="^cat:"))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("list", list_expenses))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("categories", categories_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
