# 🏠 Expense Tracker Bot

A Telegram bot for tracking shared household expenses. Register expenses, split by person, and view monthly breakdowns — all from a Telegram group chat.

## Features

- Register expenses with a quick one-liner or a guided step-by-step flow
- Categorize expenses with inline buttons (Food, Home, Transport, Health, Other)
- View all expenses, totals, and breakdowns by person or category
- Access control — only authorized users can use the bot
- Admin commands to add/remove users

## Commands

| Command | Description |
|---|---|
| `/add` | Register expense (step-by-step) |
| `/add <amount> <description>` | Register expense (quick) |
| `/add <amount> <description> @username` | Register expense paid by someone else |
| `/list` | All expenses this month |
| `/total` | Month total |
| `/mine` | My expenses this month |
| `/summary` | Breakdown by person |
| `/categories` | Breakdown by category |
| `/help` | Show all commands |

## Stack

- **Python 3** + [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21.6
- **Supabase** — Postgres database
- **Railway** — hosting (worker process, no HTTP server)

## Project Structure

```
bot.py          # command handlers and bot logic
config.py       # env vars and constants (categories, currency)
strings.py      # all user-facing messages
requirements.txt
Procfile        # Railway entry point
railway.toml    # Railway deploy config
.env.example    # env var template
```

## Setup

### 1. Create a Telegram bot

Talk to [@BotFather](https://t.me/BotFather) and create a new bot. Copy the token.

### 2. Create a Supabase project

Create two tables with RLS enabled:

```sql
CREATE TABLE expenses (
    id bigserial PRIMARY KEY,
    amount numeric NOT NULL,
    description text NOT NULL,
    paid_by text NOT NULL,
    category text,
    month int4 NOT NULL,
    year int4 NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE TABLE allowed_users (
    telegram_id bigint PRIMARY KEY,
    username text
);

ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE allowed_users ENABLE ROW LEVEL SECURITY;
```

Use the **service_role** key (not anon) so the bot can bypass RLS.

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
CURRENCY=S/
ADMIN_ID=your_telegram_user_id
```

> Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

### 4. Run locally

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python bot.py
```

## Deploy to Railway

1. Push to GitHub
2. Create a new Railway project → Deploy from GitHub repo
3. Add all env vars in the Railway dashboard
4. Railway picks up `railway.toml` automatically and runs the bot as a worker

Every `git push` to `main` triggers a redeploy.

## Access Control

The bot is restricted to authorized users only. Unauthorized users are blocked on every command.

To add a user (admin only):
```
/adduser @username <telegram_id>
```

To remove a user (admin only):
```
/removeuser @username
```

## Customization

- **Messages / Language** — all user-facing text is in `strings.py`. Translate it to any language without touching the bot logic.
- **Categories** — edit the `CATEGORIES` list in `config.py`
- **Currency** — set `CURRENCY` in `.env` (e.g. `S/`, `$`, `€`)

## Built with

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Supabase](https://supabase.com)
- [Railway](https://railway.app)
- Built with [Claude Code](https://claude.ai/code)
