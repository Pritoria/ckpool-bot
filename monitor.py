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

def send_telegram_document(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(
        url + f"?chat_id={USER_ID}&caption={caption}",
        data=data,
        headers={"Content-Type": "multipart/form-data"}
    )
    urllib.request.urlopen(req, timeout=20)

def send_telegram_photo(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(file_path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(
        url + f"?chat_id={USER_ID}&caption={caption}",
        data=data,
        headers={"Content-Type": "multipart/form-data"}
    )
    urllib.request.urlopen(req, timeout=20)

def send_telegram_buttons(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "Обновить", "callback_data": "refresh"}],
            [{"text": "Показать лог", "callback_data": "show_log"}]
        ]
    }
    payload = {"chat_id": USER_ID, "text": text, "reply_markup": json.dumps(keyboard)}
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
    except subprocess.CalledProcessError as e:
        if e.returncode == 28:
            msg = "⚠️ Пул не ответил за 40 секунд (timeout)."
        else:
            msg = "❌ Ошибка запроса к пулу: " + str(e)
        send_telegram_text(msg)
        log_event(msg)
        return
    except Exception as e:
        msg = "❌ Общая ошибка: " + str(e)
        send_telegram_text(msg)
        log_event(msg)
        return

    workers = data.get("workerCount", data.get("workers", 0))
    hashrate = data.get("hashrate1hr", "0")
    shares = data.get("shares", 0)
    bestshare = data.get("bestshare", 0)
    bestever = data.get("bestever", 0)
    lastshare = data.get("lastshare", "нет данных")

    msg = (
        "🚀 Мониторинг CKPool\n\n"
        f"🔹 Активных воркеров: *{workers}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate}*\n"
        f"🔹 Shares: *{shares}*\n"
        f"🔹 Bestshare: *{bestshare}*\n"
        f"🔹 Bestever: *{bestever}*\n"
        f"🔹 Lastshare: *{lastshare}*"
    )
    send_telegram_text(msg)
    log_event(f"Workers={workers}, Hashrate={hashrate}, Shares={shares}, Bestshare={bestshare}, Bestever={bestever}, Lastshare={lastshare}")

    # Дополнительно можно прикрепить лог или фото:
    # send_telegram_document(LOG_FILE, "История мониторинга")
    # send_telegram_photo("graph.png", "График хешрейта")
    # send_telegram_buttons("Выберите действие:")

if __name__ == "__main__":
    main()
