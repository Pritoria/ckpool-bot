import json
import ssl
import urllib.request

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = "634135028"
BTC_ADDRESS = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"


def send_telegram(text):
    url = "https://telegram.org" + BOT_TOKEN + "/sendMessage"
    payload = json.dumps(
        {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urllib.request.urlopen(req, context=ctx, timeout=10)
        print("Успех: Сигнал отправлен в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса нового API пула по прямому IP...")

    # ИСПРАВЛЕНО: Направляем запрос напрямую на рабочий IP-адрес нового сервера статистики 176.9.231.135
    url = "https://176.9.231" + BTC_ADDRESS

    # Обязательно передаем правильный Host, чтобы веб-сервер пула понял, какой сайт мы запрашиваем
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Host": "eusolostats.ckpool.org",
        },
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("Ошибка запроса к пулу по IP: " + str(e))
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
        print("Пул вернул пустой ответ.")


if __name__ == "__main__":
    main()
