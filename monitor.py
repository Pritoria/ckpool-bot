import json
import ssl
import urllib.request

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = "634135028"
BTC_ADDRESS = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"


def send_telegram(text):
    # Прямая сборка строки URL во избежание синтаксических ошибок
    url = "https://telegram.org" + BOT_TOKEN + "/sendMessage"

    payload = json.dumps(
        {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    # Игнорируем проверку SSL для Telegram
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urllib.request.urlopen(req, context=ctx, timeout=10)
        print("Успех: Сообщение успешно доставлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового API пула...")

    # ИСПОЛЬЗУЕМ НОВЫЙ АКТУАЛЬНЫЙ АДРЕС API, КОТОРЫЙ ВЫ НАШЛИ
    url = "https://ckpool.org" + BTC_ADDRESS
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    # Игнорируем проверку SSL для пула (убирает ошибку Name or service not known)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("Ошибка запроса к пулу: " + str(e))
        return

    if data:
        # Считываем переменные по новому стандарту движка CKPool
        workers = data.get("workerCount", 0)
        hashrate = data.get("hashrate1hr", "0")

        msg = (
            "🚀 **Облачный мониторинг CKPool успешно запущен!**\n\n"
            "🔹 Активных воркеров: *" + str(workers) + "*\n"
            "🔹 Хешрейт (1ч): *" + str(hashrate) + "*"
        )
        send_telegram(msg)
    else:
        print("Пул вернул пустой ответ.")


if __name__ == "__main__":
    main()
