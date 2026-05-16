import os
import json
import ssl
import urllib.request

# Бот забирает данные напрямую из панели Render, минуя текстовые файлы
BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = os.environ.get("USER_ID")
BTC_ADDRESS = os.environ.get("BTC_ADDRESS")

def send_telegram(text):
    if not BOT_TOKEN or not USER_ID:
        print("Ошибка: Токен или ID не настроены в панели Render!")
        return
        
    url = "https://telegram.org" + str(BOT_TOKEN).strip() + "/sendMessage"
    payload = json.dumps({"chat_id": str(USER_ID).strip(), "text": text, "parse_mode": "Markdown"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        urllib.request.urlopen(req, context=ctx, timeout=10)
        print("Успех: Сообщение отправлено в Telegram!")
    except Exception as e:
        print("Ошибка отправки в TG: " + str(e))

def main():
    if not BTC_ADDRESS:
        print("Ошибка: BTC адрес не настроен в панели Render!")
        return
        
    print("Запуск опроса пула по прямому IP...")
    url = "https://176.9.136" + str(BTC_ADDRESS).strip()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Host": "solo.ckpool.org"})
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("Ошибка запроса к пулу по IP: " + str(e))
        send_telegram("⚠️ Бот в облаке работает, но сам пул CKPool выдал ошибку: " + str(e))
        return

    if data:
        hashrate = data.get("hashrate1m", "0")
        workers = data.get("workers", 0)
        msg = f"🚀 **Облачный мониторинг успешно запущен!**\n\n🔹 Воркеров: *{workers}*\n🔹 Хешрейт: *{hashrate}*"
        send_telegram(msg)

if __name__ == "__main__":
    main()
