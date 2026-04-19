import os
import time
import requests
from bs4 import BeautifulSoup
import logging

# إعدادات التسجيل (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الإعدادات - يجب تعبئتها من قبل المستخدم أو عبر متغيرات البيئة
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID")
TARGET_URL = "https://adhahi.dz/register"
CHECK_INTERVAL = 300  # الفحص كل 5 دقائق (بالثواني)

def check_availability():
    """
    يقوم بفحص الموقع للبحث عن ولاية باتنة وتوفر الأضاحي.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20, verify=False) # verify=False لتخطي مشاكل SSL المؤقتة
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن كلمة "باتنة" في محتوى الصفحة
            # ملاحظة: قد يحتاج هذا الجزء لتعديل بناءً على بنية الـ HTML الدقيقة للموقع عند عمله
            page_text = soup.get_text()
            
            if "باتنة" in page_text or "Batna" in page_text:
                # هنا يمكن إضافة منطق أكثر دقة إذا كان هناك زر "حجز" أو حالة معينة
                return True, "تم العثور على ولاية باتنة في الموقع! قد تكون الأضاحي متوفرة الآن."
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
    logger.info("بدء تشغيل بوت مراقبة أضاحي العيد...")
    last_status = False
    
    while True:
        available, msg = check_availability()
        
        if available:
            if not last_status: # إرسال تنبيه فقط عند تغير الحالة من غير متوفر إلى متوفر
                alert_msg = f"🚨 *تنبيه هام!* 🚨\n\n{msg}\n\nرابط التسجيل: {TARGET_URL}"
                send_telegram_message(alert_msg)
                logger.info("تم إرسال تنبيه بالتوفر!")
            last_status = True
        else:
            logger.info(f"الفحص الدوري: {msg}")
            last_status = False
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # تنبيه أولي عند تشغيل البوت
    if TELEGRAM_TOKEN != "YOUR_BOT_TOKEN":
        send_telegram_message("✅ تم تشغيل بوت مراقبة أضاحي العيد بنجاح. سأقوم بتنبيهك فور توفر ولاية باتنة.")
    main()
