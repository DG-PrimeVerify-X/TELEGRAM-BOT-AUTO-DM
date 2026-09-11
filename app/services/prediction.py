import asyncio
from collections import Counter
from datetime import datetime, timezone

import aiohttp

ENDPOINT = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
PATTERNS = [
    "QUANTUM_WAVE_BREAK", "DRAGON_CONTINUITY_V4", "NEURAL_ENTROPY_FILTER",
    "FRACTAL_REVERSAL_SYNC", "ALGO_PRESSURE_MATRIX", "VOLATILITY_ABSORPTION",
]


def normalize(item):
    issue = str(item.get("issue") or item.get("issueNumber") or item.get("period") or item.get("IssueNumber") or item.get("issueNo") or "")
    try:
        number = int(item.get("number", item.get("openNumber", item.get("result", item.get("Number", 0)))))
    except Exception:
        number = 0
    return {"issue": issue, "number": number, "type": "BIG" if number >= 5 else "SMALL"}


def make_prediction(history, next_issue):
    # Mirrors the prediction logic used by the supplied 1M HTML, without claiming certainty.
    if len(history) < 3:
        try: y = int(str(next_issue)[-1])
        except Exception: y = 4
        y = y or 4
        return {"type": "SMALL" if y <= 4 else "BIG", "number": y, "confidence": 98.4, "pattern": PATTERNS[0], "stake": "1X BASE"}
    a = [x["type"] for x in history[:10]]
    nums = [x["number"] for x in history[:10]]
    u, pattern, streak = "SMALL", PATTERNS[0], 1
    while streak < len(a) and streak < len(a) and a[streak] == a[streak - 1]:
        streak += 1
    if streak >= 3:
        if streak > 6:
            u = "SMALL" if a[0] == "BIG" else "BIG"; pattern = "DRAGON_EXHAUSTION_REVERSAL"
        else:
            u = a[0]; pattern = "DRAGON_CONTINUITY_V4"
    elif len(a) >= 3 and a[0] != a[1] and a[1] != a[2]:
        u = "SMALL" if a[0] == "BIG" else "BIG"; pattern = "QUANTUM_WAVE_BREAK"
    else:
        u = "BIG" if a[:5].count("BIG") >= 3 else "SMALL"; pattern = "NEURAL_ENTROPY_FILTER"
    candidates = [0,1,2,3,4] if u == "SMALL" else [5,6,7,8,9]
    counts = Counter(n for n in nums if n in candidates)
    try: v = int(str(next_issue)[-2:])
    except Exception:
        try: v = int(str(next_issue)[-1:])
        except Exception: v = 0
    candidates.sort(key=lambda x: counts[x], reverse=True)
    number = candidates[v % len(candidates)]
    confidence = 97 + ((v * 7 + number * 3) % 25) / 10
    return {"type": u, "number": number, "confidence": round(confidence, 1), "pattern": pattern, "stake": "2X BOOST" if streak >= 2 else "1X SAFE"}


class PredictionService:
    def __init__(self, bot, db):
        self.bot, self.db = bot, db
        self.session = None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_history(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12))
        async with self.session.get(ENDPOINT, params={"_": int(datetime.now(timezone.utc).timestamp() * 1000)}, headers={"Cache-Control": "no-cache"}) as r:
            r.raise_for_status()
            data = await r.json(content_type=None)
        raw = data.get("data", []) if isinstance(data, dict) else []
        if isinstance(raw, dict): raw = raw.get("list", raw.get("data", []))
        return [normalize(x) for x in raw if isinstance(x, dict) and str(normalize(x)["issue"])]

    async def process_channel(self, chat_id):
        ch = await self.db.get_channel(chat_id)
        if not ch or not int(ch[10] if len(ch) > 10 else 0):
            return
        history = await self.fetch_history()
        if not history:
            return
        latest = history[0]
        await self.db.record_prediction_result(chat_id, latest["issue"], latest["number"])
        # Predict for the next period only once.
        if await self.db.prediction_exists(chat_id, latest["issue"]):
            return
        try:
            next_issue = str(int(latest["issue"]) + 1)
        except Exception:
            next_issue = latest["issue"] + "1"
        pred = make_prediction(history, next_issue)
        await self.db.save_prediction(chat_id, next_issue, pred["type"], pred["number"], pred["confidence"], pred["pattern"])
        if int(ch[5]):
            text = (
                "🤖 <b>1M AUTO PREDICTION</b>\n\n"
                f"📌 Period: <code>{next_issue}</code>\n"
                f"🔮 Signal: <b>{pred['type']}</b>\n"
                f"🔢 Number: <b>{pred['number']}</b>\n"
                f"📊 Model score: <b>{pred['confidence']}%</b>\n"
                f"🧠 Pattern: <code>{pred['pattern']}</code>\n\n"
                "⚠️ Statistical signal only — no guaranteed outcome."
            )
            await self.bot.send_message(chat_id, text)

    async def tick(self):
        channels = await self.db.prediction_channels()
        for cid in channels:
            try:
                await self.process_channel(cid)
            except Exception:
                # Keep one bad channel from stopping all other channel automations.
                continue
