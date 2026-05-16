import json
import subprocess
import urllib.request
import datetime

BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = 634135028
LOG_FILE = "monitor.log"

# --- Блок Telegram ---
def send_telegram_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    _post(url, payload)

def _post(url, payload):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сообщение доставлено!")
    except Exception as e:
        print("Ошибка отправки: " + str(e))

# --- Логирование ---
def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# --- Мониторинг CKPool ---
def main():
    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"
    url = f"https://eusolo.ckpool.org/users/{btc_address}"

    cmd = [
        "curl", "-k", "-s",
        "--connect-timeout", "10",
        "--retry", "3",
        "--retry-delay", "5",
        "-m", "40",
        "-H", "User-Agent: Mozilla/5.0",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_text = result.stdout.strip()

        if not response_text:
            msg = "⚠️ Пул недоступен или вернул пустой ответ."
            send_telegram_text(msg)
            log_event(msg)
            return
        if not response_text.startswith("{"):
            msg = "⚠️ Пул вернул не JSON."
            send_telegram_text(msg)
            log_event(msg + " Ответ: " + response_text[:200])
            return

        data = json.loads(response_text)
    except Exception as e:
        msg = "❌ Ошибка: " + str(e)
        send_telegram_text(msg)
        log_event(msg)
        return

    # Общая статистика
    workers = data.get("workerCount", 0)
    hashrate1h = data.get("hashrate1hr", "0")
    hashrate24h = data.get("hashrate24hr", "0")
    shares = data.get("shares", 0)
    staleShares = data.get("staleShares", 0)
    bestshare = data.get("bestshare", 0)
    bestever = data.get("bestever", 0)
    difficulty = data.get("difficulty", 0)
    lastshare_ts = data.get("lastshare", 0)

    if lastshare_ts:
        dt = datetime.datetime.utcfromtimestamp(lastshare_ts)
        lastshare_human = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        minutes_ago = int((datetime.datetime.utcnow() - dt).total_seconds() / 60)
        lastshare_human += f" ({minutes_ago} мин назад)"
    else:
        lastshare_human = "нет данных"

    msg = (
        "🚀 Мониторинг CKPool\n\n"
        f"🔹 Активных воркеров: *{workers}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate1h}*\n"
        f"🔹 Хешрейт (24ч): *{hashrate24h}*\n"
        f"🔹 Shares: *{shares}*\n"
        f"🔹 StaleShares: *{staleShares}*\n"
        f"🔹 Bestshare: *{bestshare}*\n"
        f"🔹 Bestever: *{bestever}*\n"
        f"🔹 Difficulty: *{difficulty}*\n"
        f"🔹 Lastshare: *{lastshare_human}*"
    )

    # --- Детализация по воркерам ---
    workers_data = data.get("workers", {})
    for name, stats in workers_data.items():
        w_hashrate = stats.get("hashrate1hr", "0")
        w_shares = stats.get("shares", 0)
        w_bestshare = stats.get("bestshare", 0)
        w_lastshare_ts = stats.get("lastshare", 0)

        if w_lastshare_ts:
            dt = datetime.datetime.utcfromtimestamp(w_lastshare_ts)
            w_lastshare_human = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            minutes_ago = int((datetime.datetime.utcnow() - dt).total_seconds() / 60)
            w_lastshare_human += f" ({minutes_ago} мин назад)"
        else:
            w_lastshare_human = "нет данных"

        msg += (
            f"\n\n👷 Воркер: *{name}*\n"
            f"   🔹 Хешрейт (1ч): *{w_hashrate}*\n"
            f"   🔹 Shares: *{w_shares}*\n"
            f"   🔹 Bestshare: *{w_bestshare}*\n"
            f"   🔹 Lastshare: *{w_lastshare_human}*"
        )

    send_telegram_text(msg)
    log_event(msg.replace
