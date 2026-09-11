# Telegram Admin Bot — Modular Multi-Channel

Features: public dashboard, server-side authorization, Super Admin/admin permissions, multi-channel manager, bot-admin verification, per-channel Auto Accept/Auto DM/Auto Post/Auto Reaction, broadcast, post sender, scheduler, statistics, premium custom emoji, health and backup hooks.

## Setup
Copy `.env.example` to `.env`, set BOT_TOKEN and SUPER_ADMIN_ID. OWNER_USERNAME controls the Contact Owner button.

## Channel workflow
1. Add bot as channel admin with required permissions.
2. Super Admin: `/addchannel CHANNEL_ID` (or reply to a forwarded channel post with `/addchannel`).
3. `/addadmin USER_ID permissions`
4. `/assignchannel ADMIN_ID CHANNEL_ID`
5. `/channelsettings CHANNEL_ID` to configure channel automation.

All callbacks/actions are authorized server-side. `/start` is public and opens the dashboard; unauthorized actions are blocked.
