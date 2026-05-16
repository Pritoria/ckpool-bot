import json
import subprocess
import urllib.request


def send_telegram(text):
    # Прямой URL API Telegram
    bot_token = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
    user_id = "634135028"

    url = "https://telegram.org" + bot_token + "/sendMessage"
    payload = json.dumps(
        {"chat_id": user_id, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    try:
        # Отправляем в TG через стандартный urllib (к Telegram DNS работает нормально)
        urllib.request.urlopen(req, timeout=10)
        print("Успех: Сообщение успешно доставлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового API пула через системный cURL...")

    btc_address = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"
    url = "https://176.9.231" + btc_address

    # Используем системный cURL в обход всех багов Python DNS.
    # Флаг -k отключает проверку SSL, а -H передает правильный Host домена.
    cmd = [
        "curl",
        "-k",
        "-s",
        "-m",
        "15",
        "-H",
        "Host: eusolostats.ckpool.org",
        "-H",
        "User-Agent: Mozilla/5.0",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_text = result.stdout
        data = json.loads(response_text)
    except Exception as e:
        print("Критическая ошибка cURL запроса к пулу: " + str(e))
        return

    if data:
        workers = data.get("workerCount", 0)
        hashrate = data.get("hashrate1hr", "0")

        msg = (
            "🚀 **Облачный мониторинг CKPool успешно запущен!**\n\n"
            "🔹 Активных воркеров: *" + str(workers) + "*\n"
            "🔹 Хешрейт (1ч): *" + str(hashrate) + "*"
        )
        send_telegram(msg)
    else:
        print("Пул вернул пустой ответ через cURL.")


if __name__ == "__main__":
    main()
