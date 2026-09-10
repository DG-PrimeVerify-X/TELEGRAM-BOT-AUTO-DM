# DgAutoaccept Modular Telegram Admin Bot

## Core rules
- Super Admin is the configured `SUPER_ADMIN_ID` and has full control.
- Normal admins receive only permissions explicitly granted by Super Admin.
- Channel ownership is NOT required for bot-panel access.
- Channel admin status does NOT automatically grant bot-panel access.
- Post Sender supports Channel or All Users.
- Broadcast supports All Users and arbitrary Telegram message/media types.
- Schedule Later supports Channel or All Users.
- Auto Reaction ON reacts to every new channel post received by the bot; OFF stops future automatic reactions.
- Custom emoji reaction can be configured with a valid custom emoji ID. Paid reactions are not supported by bots.
- Premium/custom emoji UI uses Telegram custom-emoji entities with a normal emoji fallback.

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The database schema is migration-safe for the scheduled-post target columns.
