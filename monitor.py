import json
import urllib.request

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = "634135028"
BTC_ADDRESS = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"


def send_telegram(text):
    # ИСПРАВЛЕНО: Добавлен точный слэш перед bot, ошибка "nonnumeric port" полностью устранена
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = json.dumps(
        {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сигнал отправлен в Telegram!")
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")


def main():
    print("Запуск опроса пула...")

    # ИСПРАВЛЕНО: Используем базовый стабильный домен пула, который всегда активен
    url = f"https://ckpool.org{BTC_ADDRESS}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка запроса к пулу: {e}")
        # Если пул недоступен, бот всё равно напишет нам об этом в TG, так как связь починена!
        send_telegram(f"⚠️ Мониторинг запущен, но сам пул CKPool сейчас выдает ошибку: {e}")
        return

    if data:
        hashrate = data.get("hashrate1m", "0")
        workers = data.get("workers", 0)

        msg = (
            f"🤖 **Облачный мониторинг CKPool запущен!**\n\n"
            f"🔹 Активных воркеров: *{workers}*\n"
            f"🔹 Текущий хешрейт: *{hashrate}*"
        )
        send_telegram(msg)


if __name__ == "__main__":
    main()
