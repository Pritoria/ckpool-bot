import json
import ssl
import urllib.request

# --- НАСТРОЙКИ ---
# ВНИМАНИЕ: Проверьте, чтобы токен и ID были строго внутри кавычек, без пробелов!
BOT_TOKEN = "8621424949:AAE0RGMEotmYEfo8I0OYyjB0gX8xPDu6JXw"
USER_ID = "634135028"
BTC_ADDRESS = "bc1qr74sk0g8d9tt5549xgp9w8k5l8440qjd8r8dtu"


def send_telegram(text):
    # Собираем ссылку без фигурных скобок, чтобы исключить ошибку nonnumeric port
    url = "https://telegram.org" + BOT_TOKEN + "/sendMessage"

    payload = json.dumps(
        {"chat_id": USER_ID, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )

    # Отключаем проверку SSL для Telegram на случай блокировок облака
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urllib.request.urlopen(req, context=ctx, timeout=10)
        print("Успех: Сигнал отправлен в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))


def main():
    print("Запуск опроса пула по прямому IP без проверки SSL...")

    # Делаем запрос напрямую к европейскому IP пула
    url = "https://176.9.136" + BTC_ADDRESS
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Host": "solo.ckpool.org"}
    )

    # ИСПРАВЛЕНО: Отключаем проверку SSL (hostname), чтобы убрать ошибку Name or service not known
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("Ошибка запроса к пулу по IP: " + str(e))
        # Так как отправка в TG теперь железно починена, бот пришлет отчет об ошибке пула
        send_telegram(
            "⚠️ Бот в облаке работает, но сам пул CKPool выдал ошибку: "
            + str(e)
        )
        return

    if data:
        hashrate = data.get("hashrate1m", "0")
        workers = data.get("workers", 0)

        msg = (
            "🚀 **Облачный мониторинг CKPool успешно запущен!**\n\n"
            "🔹 Активных воркеров: *" + str(workers) + "*\n"
            "🔹 Ваш хешрейт: *" + str(hashrate) + "*"
        )
        send_telegram(msg)


if __name__ == "__main__":
    main()
