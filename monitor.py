import json
import subprocess
import urllib.request


def send_telegram(text, use_markdown=True):
    bot_token = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
    user_id = 634135028

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {"chat_id": user_id, "text": text}

    # ИСПРАВЛЕНО: Включаем разметку только для красивого финального сообщения,
    # чтобы сырые ошибки пула не вызывали ошибку 400 Bad Request
    if use_markdown:
        payload["parse_mode"] = "Markdown"

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сообщение успешно доставлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового API пула через системный cURL...")

    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"

    # ИСПРАВЛЕНО: Указан точный адрес API (/api/user/) и прямой IP для обхода DNS-блокировок
    url = f"https://176.9.231{btc_address}"

    cmd = [
        "curl",
        "-k",
        "-s",
        "-m",
        "15",
        "-H",
        "Host: eusolostats.ckpool.org",  # Обязательно передаем Host
        "-H",
        "User-Agent: Mozilla/5.0",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_text = result.stdout.strip()

        if not response_text:
            send_telegram("⚠️ Пул недоступен или вернул пустой ответ.", FALSE)
            return

        if not response_text.startswith("{"):
            send_telegram(
                "⚠️ Пул вернул не JSON. Ответ:\n" + response_text[:150], False
            )
            return

        data = json.loads(response_text)
    except Exception as e:
        send_telegram("❌ Ошибка запроса к пулу: " + str(e), False)
        return

    workers = data.get("workerCount", 0)

    # ИСПРАВЛЕНО: Движок пула может отдавать хешрейт как число или как строку (например, "10.10 TH/s").
    # Приводим к строке, чтобы f-строка Python не ломалась.
    hashrate = str(data.get("hashrate1hr", "0"))

    msg = (
        "🚀 **Облачный мониторинг CKPool успешно запущен!**\n\n"
        f"🔹 Активных воркеров: *{workers}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate}*"
    )
    send_telegram(msg, True)


if __name__ == "__main__":
    main()
