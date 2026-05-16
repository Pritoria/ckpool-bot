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
    url = f"https://ckpool.org/users/{btc_address}"

    # Добавляем -w "%{time_total}" чтобы измерить время ответа
    cmd = [
        "curl",
        "-k",
        "-s",
        "-m", "40",
        "-w", "%{time_total}",
        "-H", "User-Agent: Mozilla/5.0",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        # Последние цифры — это время ответа
        if "\n" in output:
            response_text, time_total = output.rsplit("\n", 1)
        else:
            response_text, time_total = output, "?"

        if not response_text:
            send_telegram(f"⚠️ Пул недоступен или вернул пустой ответ.\n⏱ Время ответа: {time_total} сек.")
            return

        if not response_text.startswith("{"):
            send_telegram(f"⚠️ Пул вернул не JSON.\n⏱ Время ответа: {time_total} сек.\nОтвет:\n{response_text[:200]}")
            return

        data = json.loads(response_text)
    except subprocess.CalledProcessError as e:
        if e.returncode == 28:
            send_telegram("⚠️ Пул не ответил за 40 секунд (timeout).")
        else:
            send_telegram("❌ Ошибка запроса к пулу: " + str(e))
        return
    except Exception as e:
        send_telegram("❌ Общая ошибка: " + str(e))
        return

    workers = data.get("workerCount", 0)
    hashrate = data.get("hashrate1hr", "0")

    msg = (
        "🚀 **Мониторинг CKPool**\n\n"
        f"🔹 Активных воркеров: *{workers}*\n"
        f"🔹 Хешрейт (1ч): *{hashrate}*\n"
        f"⏱ Время ответа пула: {time_total} сек."
    )
    send_telegram(msg)


if __name__ == "__main__":
    main()
