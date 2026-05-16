import json
import subprocess
import urllib.request


def send_telegram(text):
    bot_token = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
    user_id = 634135028

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сообщение успешно доставлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового европейского API пула...")

    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"
    url = f"https://ckpool.org/users/{btc_address}"  # ← исправлено

    cmd = [
        "curl",
        "-k",
        "-s",
        "-m", "40",
        "-H", "User-Agent: Mozilla/5.0",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_text = result.stdout.strip()

        if not response_text:
            send_telegram("⚠️ Пул недоступен или вернул пустой ответ.")
            return

        if not response_text.startswith("{"):
            send_telegram("⚠️ Пул вернул не JSON. Ответ:\n" + response_text[:200])
            return

        data = json.loads(response_text)
    except Exception as e:
        send_telegram("❌ Ошибка запроса к пулу: " + str(e))
        return

    workers = data.get("workerCount", 0)
    hashrate = data.get("hashrate1hr", "0")

    msg = (
        "🚀 **Облачный мониторинг CKPool успешно запущен!**\n\n"
        f"🔹 Активных воркеров: *{workers}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate}*"
    )
    send_telegram(msg)


if __name__ == "__main__":
    main()
