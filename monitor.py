import json
import subprocess
import urllib.request
import datetime

BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = 634135028
LOG_FILE = "monitor.log"

# --- Telegram ---
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

# --- Парсер хешрейта ---
def parse_hashrate(value):
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return 0.0
    val = value.upper().strip()
    try:
        if val.endswith("T"):
            return float(val[:-1]) * 1e12
        elif val.endswith("G"):
            return float(val[:-1]) * 1e9
        elif val.endswith("M"):
            return float(val[:-1]) * 1e6
        elif val.endswith("K"):
            return float(val[:-1]) * 1e3
        else:
            return float(val)
    except:
        return 0.0

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

