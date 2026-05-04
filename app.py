import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Faltan variables TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
        return False
    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")
        return False

def format_signal(data: dict) -> str:
    signal  = data.get("signal",  "---")
    ticker  = data.get("ticker",  "---")
    tf      = data.get("tf",      "---")
    score   = data.get("score",   "---")
    conf    = data.get("conf",    "---")
    entry   = data.get("entry",   "---")
    sl      = data.get("sl",      "---")
    tp1     = data.get("tp1",     "---")
    tp2     = data.get("tp2",     "---")
    tp3     = data.get("tp3",     "---")
    tp4     = data.get("tp4",     "---")
    tp5     = data.get("tp5",     "---")
    bull    = data.get("bull",    "---")
    bear    = data.get("bear",    "---")
    time_s  = data.get("time",    "---")

    # Emoji según tipo de señal
    sig_upper = signal.upper()
    if "BUY" in sig_upper or "LARGO" in sig_upper or "ALCISTA" in sig_upper:
        emoji = "🟢"
        direction = "LARGO / BUY"
    elif "SELL" in sig_upper or "CORTO" in sig_upper or "BAJISTA" in sig_upper:
        emoji = "🔴"
        direction = "CORTO / SELL"
    elif "RETEST" in sig_upper:
        emoji = "🟠"
        direction = signal
    elif "FIN" in sig_upper or "IMPULSO" in sig_upper:
        emoji = "⚡"
        direction = signal
    else:
        emoji = "📊"
        direction = signal

    # Emoji score
    try:
        score_val = int(str(score).replace("%",""))
        if score_val >= 75:
            score_emoji = "🔥"
        elif score_val >= 55:
            score_emoji = "✅"
        else:
            score_emoji = "⚠️"
    except:
        score_emoji = "📊"

    msg = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>NEXUS ALGO PRO — SEÑAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji} <b>{direction}</b> — {ticker} {tf}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{score_emoji} Score: <b>{score}</b>\n"
        f"🎯 Confluencias: <b>{conf}</b>\n"
        f"📈 Bull Score: <b>{bull}</b>  |  📉 Bear Score: <b>{bear}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Entry:  <b>{entry}</b>\n"
        f"🛡️ SL:     <b>{sl}</b>\n"
        f"🎯 TP1:   <b>{tp1}</b>\n"
        f"🎯 TP2:   <b>{tp2}</b>\n"
        f"🎯 TP3:   <b>{tp3}</b>\n"
        f"🏆 TP4:   <b>{tp4}</b>\n"
        f"👑 TP5:   <b>{tp5}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {time_s}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    return msg

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True) or {}
        if not data:
            # TradingView puede mandar texto plano
            raw = request.data.decode("utf-8", errors="ignore")
            send_telegram(f"📩 Alerta NEXUS:\n{raw}")
            return jsonify({"ok": True})

        msg = format_signal(data)
        ok  = send_telegram(msg)
        return jsonify({"ok": ok})
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return "NEXUS Telegram Bot activo ✅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
