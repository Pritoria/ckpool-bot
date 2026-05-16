import json
import subprocess
import urllib.request
import datetime

BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = 634135028
LOG_FILE = "monitor.log"

def send_telegram_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10)

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"
    url = f"https://eusolo.ckpool.org/users/{btc_address}"

    cmd = ["curl", "-s", url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout.strip())
    except Exception as e:
        msg = "❌ Ошибка: " + str(e)
        send_telegram_text(msg)
        log_event(msg)
        return

    # Общая статистика
    workers_count = data.get("workerCount", 0)
    hashrate1h = data.get("hashrate1hr", "0")
    shares = data.get("shares", 0)
    bestshare = data.get("bestshare", 0)
    bestever = data.get("bestever", 0)

    msg = (
        "🚀 Мониторинг CKPool\n\n"
        f"🔹 Активных воркеров: *{workers_count}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate1h}*\n"
        f"🔹 Shares: *{shares}*\n"
        f"🔹 Bestshare: *{bestshare}*\n"
        f"🔹 Bestever: *{bestever}*"
    )

    # --- Детализация по воркерам ---
    workers_data = data.get("workers", {})
    if isinstance(workers_data, dict):  # только если это словарь
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
                minutes_ago = None

            msg += (
                f"\n\n👷 Воркер: *{name}*\n"
                f"   🔹 Хешрейт (1ч): *{w_hashrate}*\n"
                f"   🔹 Shares: *{w_shares}*\n"
                f"   🔹 Bestshare: *{w_bestshare}*\n"
                f"   🔹 Lastshare: *{w_lastshare_human}*"
            )

            # --- Автоматический алерт ---
            if w_hashrate == "0" or (minutes_ago is not None and minutes_ago > 30):
                alert = (
                    f"⚠️ Воркер {name} неактивен!\n"
                    f"   Хешрейт: {w_hashrate}\n"
                    f"   Последний share: {w_lastshare_human}"
                )
                send_telegram_text(alert)
                log_event("ALERT: " + alert)

    send_telegram_text(msg)
    log_event(msg.replace("\n", " "))

if __name__ == "__main__":
    main()

