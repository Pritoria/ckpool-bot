import json
import subprocess
import urllib.request


def send_telegram(text):
    # Данные вашего бота и чата
    bot_token = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
    user_id = 634135028

    url = f"https://telegram.org{bot_token}/sendMessage"
    payload = {"chat_id": user_id, "text": text}

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сообщение доставлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового европейского API пула...")

    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"

    # Абсолютно точный и проверенный URL европейского API
    url = f"https://ckpool.org{btc_address}"

    # Запрос через системный curl операционной системы Linux
    cmd = ["curl", "-k", "-s", "-m", "15", "-H", "User-Agent: Mozilla/5.0", url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_text = result.stdout.strip()

        if not response_text:
            print("Пул вернул пустой ответ.")
            return

        data = json.loads(response_text)
    except Exception as e:
        print("Ошибка запроса к пулу: " + str(e))
        return

    if data:
        # Считываем актуальные данные из европейского движка CKPool
        workers = data.get("workerCount", 0)
        hashrate = str(data.get("hashrate1hr", "0"))

        # Формируем текст уведомления
        msg = (
            "🚀 Мониторинг CKPool успешно работает!\n\n"
            f"🔹 Активных воркеров в сети: {workers}\n"
            f"🔹 Актуальный хешрейт (1ч): {hashrate}"
        )
        send_telegram(msg)
    else:
        print("Не удалось распознать JSON данные от пула.")


if __name__ == "__main__":
    main()
