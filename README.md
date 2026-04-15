# 🏠 Expense Tracker Bot

![Home Expenses Banner](assets/banner.png)

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
- **Oracle Cloud (OCI)** — hosting (Always Free tier, VM.Standard.E2.1.Micro)

## Project Structure

```
bot.py          # command handlers and bot logic
config.py       # env vars and constants (categories, currency)
strings.py      # all user-facing messages
requirements.txt
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

## Deploy to OCI (Oracle Cloud Free Tier)

### 1. Create an OCI instance

- Shape: `VM.Standard.E2.1.Micro` (Always Free)
- OS: Ubuntu 20.04
- Create a VCN with internet connectivity before creating the instance
- Assign a public IPv4 address

### 2. Set up the server

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/your-username/expense-tracker-bot.git
cd expense-tracker-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create the `.env` file on the server

```bash
nano .env
```

### 4. Run as a systemd service

```bash
sudo nano /etc/systemd/system/expense-bot.service
```

```ini
[Unit]
Description=Expense Tracker Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/expense-tracker-bot
EnvironmentFile=/home/ubuntu/expense-tracker-bot/.env
ExecStart=/home/ubuntu/expense-tracker-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable expense-bot
sudo systemctl start expense-bot
```

### 5. Auto-deploy with GitHub Actions

Add these secrets to your GitHub repo (Settings → Secrets → Actions):

- `OCI_HOST` — your instance public IP
- `OCI_SSH_KEY` — contents of your SSH private key

Every push to `main` will automatically pull and restart the bot.

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
- [Oracle Cloud](https://www.oracle.com/cloud/free/)
- Built with [Claude Code](https://claude.ai/code)
