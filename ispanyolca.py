import json
import os
import google.generativeai as genai
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- AYARLAR ---
# API anahtarını Railway'den alacak şekilde düzenledik
API_ANAHTARI = os.environ.get("GEMINI_API_KEY") 
BOT_TOKEN = "8998004971:AAHgf6rtjZvy4ZKehrPgUq5HrTqQdg-wSek"

genai.configure(api_key=API_ANAHTARI)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_offline_data(konu_key):
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data.get(konu_key, None)
            except:
                return None
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    klavye = [
        [KeyboardButton("🎓 Alfabe"), KeyboardButton("🎓 Sayılar")],
        [KeyboardButton("🎓 Renkler"), KeyboardButton("🎓 Fiiller")]
    ]
    markup = ReplyKeyboardMarkup(klavye, resize_keyboard=True)
    await update.message.reply_text("👑 **Diyar Borak Akademi:** Hangi konuyu fethediyoruz?", reply_markup=markup)

async def mesaj_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("🎓 ", "").lower()
    
    # 1. Önce Offline Veriyi Kontrol Et
    offline_veri = get_offline_data(text)
    
    if offline_veri:
        await update.message.reply_text(f"📖 **Offline Mod:**\n{offline_veri['icerik']}\n\n❓ Soru: {offline_veri['soru']}")
    else:
        # 2. İnternet Varsa Gemini'a Bağlan
        if not API_ANAHTARI:
            await update.message.reply_text("⚠️ Hata: API anahtarı yapılandırılmamış!")
            return
            
        await update.message.reply_text(f"🚀 İnternet üzerinden {text} dersi hazırlanıyor...")
        try:
            prompt = f"İspanyolca {text} konusu için hardcore ders, hikaye ve soru hazırla."
            cevap = model.generate_content(prompt)
            await update.message.reply_text(cevap.text)
        except Exception as e:
            await update.message.reply_text("⚠️ İnternet yok veya API anahtarı geçersiz!")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_al))
    print("🚀 Diyar Borak Akademi Hibrit Modda Çalışıyor!")
    app.run_polling()