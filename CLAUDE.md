# Expense Tracker Bot

> **Note for Claude:** Do not include personal information in this file — no real Telegram IDs, usernames, API keys, or any user-specific data. This file is public.

Telegram bot for shared household expense tracking via a group chat.

## Stack
- Python 3
- python-telegram-bot 21.6
- Supabase (Postgres) — database
- Oracle Cloud (OCI) — hosting (Always Free, VM.Standard.E2.1.Micro)
- python-dotenv — env vars

## Project Structure
- `bot.py` — all command handlers and bot logic
- `config.py` — env vars and app constants (CATEGORIES, CURRENCY, etc.)
- `strings.py` — all user-facing messages (translate here for other languages)
- `requirements.txt` — dependencies
- `.env` — local secrets (never commit)
- `.env.example` — env var template

## Environment Variables
| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase **service_role** key (not anon) |
| `CURRENCY` | Currency prefix (e.g. `S/`, `$`, `€`) |
| `ADMIN_ID` | Admin's Telegram user ID (get it from @userinfobot) |

## Supabase Tables

### expenses
| Column | Type |
|---|---|
| id | int8 (PK) |
| amount | numeric |
| description | text |
| paid_by | text (Telegram username) |
| category | text |
| month | int4 |
| year | int4 |
| created_at | timestamptz |

### allowed_users
| Column | Type |
|---|---|
| telegram_id | int8 (PK) |
| username | text |

Both tables have RLS enabled. The service_role key bypasses RLS — never use the anon key.

## Commands
| Command | Description | Access |
|---|---|---|
| `/add` | Step-by-step expense flow | All users |
| `/add <amount> <description>` | Quick one-liner | All users |
| `/add <amount> <description> @username` | Register expense for someone else | All users |
| `/list` | List all expenses this month | All users |
| `/total` | Month total | All users |
| `/mine` | My expenses this month | All users |
| `/summary` | Breakdown by person | All users |
| `/categories` | Breakdown by category | All users |
| `/help` | Show help | All users |
| `/adduser @username <telegram_id>` | Add allowed user | Admin only |
| `/removeuser @username` | Remove allowed user | Admin only |

## Access Control
- All commands check `allowed_users` table or `ADMIN_ID`
- Unauthorized users get blocked on every command and callback
- Only admin can add/remove users

## Running Locally
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python bot.py
```

## Deploying to OCI
- Bot runs as a systemd service (`expense-bot.service`)
- GitHub Actions auto-deploys on every push to `main` via SSH
- Secrets needed: `OCI_HOST`, `OCI_SSH_KEY` (set in GitHub repo settings)
- Service managed with: `sudo systemctl start|stop|restart expense-bot`

## Server Recovery (if instance is wiped)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/nowjordanhappy/expense-tracker-bot.git
cd expense-tracker-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env  # add BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY, CURRENCY, ADMIN_ID
sudo tee /etc/systemd/system/expense-bot.service << 'EOF'
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
EOF
sudo systemctl daemon-reload
sudo systemctl enable expense-bot
sudo systemctl start expense-bot
```

## Adding Messages
All user-facing text is in `strings.py`. Edit there — do not hardcode strings in `bot.py`.

## Adding Categories
Edit the `CATEGORIES` list in `config.py`. Each entry is a tuple: `("🏷 Label", "value")`.
