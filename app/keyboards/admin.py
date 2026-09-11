from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

def main_menu(owner=""):
    rows=[
      [InlineKeyboardButton(text="🆕 New Requests",callback_data="req:new"),InlineKeyboardButton(text="🕐 Old/Pending",callback_data="req:old")],
      [InlineKeyboardButton(text="🤖 Auto-DM",callback_data="set:dm"),InlineKeyboardButton(text="⚡ Auto Accept",callback_data="set:accept")],
      [InlineKeyboardButton(text="📣 Post Sender",callback_data="post:start"),InlineKeyboardButton(text="📤 Auto Post",callback_data="set:post")],
      [InlineKeyboardButton(text="⏰ Scheduled Posts",callback_data="post:schedules"),InlineKeyboardButton(text="📢 Broadcast",callback_data="broadcast:start")],
      [InlineKeyboardButton(text="❤️ Auto Reaction",callback_data="reaction:page"),InlineKeyboardButton(text="🤖 1M Prediction",callback_data="set:prediction")],
      [InlineKeyboardButton(text="📢 Channels",callback_data="channels:list"),InlineKeyboardButton(text="👥 Users",callback_data="users:stats")],
      [InlineKeyboardButton(text="📊 Statistics",callback_data="users:stats"),InlineKeyboardButton(text="👨‍💼 Admins",callback_data="admins:help")],
      
      [InlineKeyboardButton(text="⚙️ Settings",callback_data="settings"),InlineKeyboardButton(text="💎 Premium Emoji",callback_data="premium:page")],
      [InlineKeyboardButton(text="💾 Backup",callback_data="backup"),InlineKeyboardButton(text="❤️ Health",callback_data="health")]
    ]
    if owner:
        rows.append([InlineKeyboardButton(text="📞 CONTACT US FOR BOT",url="https://t.me/"+owner.lstrip("@"))])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def access_keyboard(owner):
    return InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="📞 CONTACT OWNER",url="https://t.me/"+owner.lstrip("@"))]
    ])

def channels_keyboard(channels):
    rows=[[InlineKeyboardButton(text=name[:35],callback_data=f"post:channel:{cid}")] for cid,name in channels]
    rows.append([InlineKeyboardButton(text="👥 All Users",callback_data="post:allusers")])
    rows.append([InlineKeyboardButton(text="❌ Cancel",callback_data="post:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def post_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="🚀 Send Now",callback_data="post:sendnow"),InlineKeyboardButton(text="⏰ Schedule",callback_data="post:schedule")],
      [InlineKeyboardButton(text="❌ Cancel",callback_data="post:cancel")]
    ])

def reaction_keyboard(enabled):
    return InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text=f"Auto Reaction: {'🟢 ON' if enabled else '🔴 OFF'}",callback_data="reaction:toggle")],
      [InlineKeyboardButton(text="👍 Set 👍",callback_data="reaction:set:👍"),InlineKeyboardButton(text="❤️ Set ❤️",callback_data="reaction:set:❤️")],
      [InlineKeyboardButton(text="🔥 Set 🔥",callback_data="reaction:set:🔥"),InlineKeyboardButton(text="🎉 Set 🎉",callback_data="reaction:set:🎉")],
      [InlineKeyboardButton(text="⬅️ Back",callback_data="back")]
    ])
