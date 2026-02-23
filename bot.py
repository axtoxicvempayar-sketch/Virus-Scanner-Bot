import os
import requests
import time
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ওয়েব সার্ভার সেটআপ (বট অমর করার জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "AX Scanner is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- আপনার তথ্যসমূহ ---
BOT_TOKEN = "8776575060:AAGzejTLLTdtxCatut09oSw45QB7ME1OkIc"
VT_API_KEY = "8792b493d224e4bf5b19812e231ad8b4072dbf5562b818b5cf14b11800cc23a7"
DEVELOPER_ID = "@ax_abir_999"

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"**🛡️ স্বাগতম! আমি আপনার ডিজিটাল বডিগার্ড।**\n\n"
        f"**যেকোনো সন্দেহজনক লিঙ্ক বা APK ফাইল আমাকে পাঠান। আমি চেক করে দেখব তা নিরাপদ কি না।**\n"
        f"⚠️ **নিজেকে সুরক্ষিত রাখুন:** ইন্টারনেটের সব লিঙ্ক নিরাপদ নয়। স্ক্যান না করে কোনো কিছু ওপেন করবেন না।\n\n"
        f"**👨‍💻 Developer:** **{DEVELOPER_ID}**"
    )
    buttons = [[InlineKeyboardButton("👨‍💻 Contact Developer", url=f"https://t.me/{DEVELOPER_ID.replace('@', '')}")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

# লিঙ্ক স্ক্যান করার ফাংশন
async def scan_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return
    
    status_msg = await update.message.reply_text("🔎 **লিঙ্কটি বিশ্লেষণ করা হচ্ছে... একটু অপেক্ষা করুন।**", parse_mode='Markdown')
    
    headers = {"x-apikey": VT_API_KEY}
    vt_url = "https://www.virustotal.com/api/v3/urls"
    
    try:
        response = requests.post(vt_url, data={"url": url}, headers=headers)
        if response.status_code == 200:
            analysis_id = response.json()['data']['id']
            time.sleep(3)
            result_req = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers)
            stats = result_req.json()['data']['attributes']['stats']
            
            malicious = stats['malicious']
            suspicious = stats['suspicious']
            
            if malicious > 0 or suspicious > 0:
                result_text = f"❌ **বিপদ! এই লিঙ্কটি নিরাপদ নয়!**\n\n⚠️ **ক্ষতিকর ইঞ্জিন পাওয়া গেছে:** `{malicious}`"
            else:
                result_text = f"✅ **অভিনন্দন! এই লিঙ্কটি সম্পূর্ণ নিরাপদ।**"
            
            await status_msg.edit_text(result_text + f"\n\n**👨‍💻 Developer:** **{DEVELOPER_ID}**", parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ **API লিমিট শেষ অথবা ভুল লিঙ্ক।**")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **এরর:** `{str(e)}`", parse_mode='Markdown')

# ফাইল স্ক্যান করার ফাংশন
async def scan_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 **ফাইল স্ক্যানিং ফিচারটি শীঘ্রই আসছে...**\n\n**আপাতত লিঙ্ক স্ক্যান করুন।**", parse_mode='Markdown')

def main():
    # বট রান করার আগে Keep Alive সার্ভার চালু করা
    keep_alive() 
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_link))
    app.add_handler(MessageHandler(filters.Document.ALL, scan_file))
    
    print("🚀 AX Virus Scanner Bot is Online!")
    app.run_polling()

if __name__ == '__main__':
    main()
