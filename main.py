import os
import time
import requests
from bs4 import BeautifulSoup
import logging
import sys

# إعدادات التسجيل (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# الإعدادات - يتم جلبها من متغيرات البيئة في Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_URL = "https://adhahi.dz/register"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # الفحص كل 5 دقائق افتراضياً

def check_availability():
    """
    يقوم بفحص الموقع للبحث عن ولاية باتنة وتوفر الأضاحي.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
    }
    
    try:
        # استخدام verify=False لتجنب مشاكل SSL المؤقتة في الموقع
        response = requests.get(TARGET_URL, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # البحث عن كلمة "باتنة" أو "Batna"
            if "باتنة" in page_text or "Batna" in page_text:
                return True, "🚨 تم العثور على ولاية باتنة في الموقع! قد تكون الأضاحي متوفرة الآن."
            else:
                return False, "الموقع يعمل ولكن ولاية باتنة غير مدرجة حالياً."
        else:
            return False, f"الموقع لا يستجيب بشكل صحيح. كود الحالة: {response.status_code}"
            
    except Exception as e:
        logger.error(f"خطأ أثناء محاولة الاتصال بالموقع: {e}")
        return False, f"فشل الاتصال بالموقع: {str(e)}"

def send_telegram_message(message):
    """
    إرسال رسالة تنبيه عبر تلغرام.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.error("TELEGRAM_TOKEN أو CHAT_ID غير محددين في متغيرات البيئة!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة تلغرام: {e}")

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.critical("خطأ: يجب ضبط TELEGRAM_TOKEN و CHAT_ID في إعدادات Railway (Variables).")
        return

    logger.info("🚀 بدء تشغيل بوت مراقبة أضاحي العيد...")
    send_telegram_message("✅ تم تشغيل بوت مراقبة أضاحي العيد بنجاح على Railway. سأقوم بتنبيهك فور توفر ولاية باتنة.")
    
    last_status = False
    
    while True:
        available, msg = check_availability()
        
        if available:
            if not last_status:
                alert_msg = f"🚨 *تنبيه هام!* 🚨\n\n{msg}\n\nرابط التسجيل: {TARGET_URL}"
                send_telegram_message(alert_msg)
                logger.info("✅ تم إرسال تنبيه بالتوفر!")
            last_status = True
        else:
            logger.info(f"🔍 فحص دوري: {msg}")
            last_status = False
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
