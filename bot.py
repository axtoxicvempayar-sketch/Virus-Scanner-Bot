import os
import requests
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ১. বটের প্রাণ (Keep Alive System) ---
app = Flask('')

@app.route('/')
def home():
    return "AX SCANNER IS LIVE! 🚀"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- ২. কনফিগারেশন ---
BOT_TOKEN = "8776575060:AAGzejTLLTdtxCatut09oSw45QB7ME1OkIc"
VT_API_KEY = "8792b493d224e4bf5b19812e231ad8b4072dbf5562b818b5cf14b11800cc23a7"
DEVELOPER = "@ax_abir_999"

# --- ৩. কমান্ডসমূহ ---

# /start কমান্ড (সুন্দর বোল্ড ডিজাইন)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        f"🛡️ **AX VIRUS SCANNER BOT**\n\n"
        f"**আপনার ডিজিটাল সুরক্ষায় আমরা সবসময় সজাগ!**\n"
        f"**যেকোনো ফাইল বা লিঙ্ক নিরাপদ কি না জানতে আমাকে পাঠান।**\n\n"
        f"👨‍💻 **Developer:** {DEVELOPER}"
    )
    keyboard = [[InlineKeyboardButton("👨‍💻 Contact Developer", url=f"https://t.me/ax_abir_999")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

# লিঙ্ক স্ক্যানিং
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("http"):
        msg = await update.message.reply_text("🔎 **বিশ্লেষণ করা হচ্ছে... অপেক্ষা করুন।**", parse_mode='Markdown')
        
        url = "https://www.virustotal.com/api/v3/urls"
        payload = {"url": text}
        headers = {"x-apikey": VT_API_KEY}
        
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                # স্ক্যান রেজাল্টের জন্য ৩ সেকেন্ড ওয়েট
                await asyncio.sleep(3)
                result_id = response.json()['data']['id']
                result_url = f"https://www.virustotal.com/api/v3/analyses/{result_id}"
                final_res = requests.get(result_url, headers=headers).json()
                
                stats = final_res['data']['attributes']['stats']
                malicious = stats['malicious']
                
                if malicious > 0:
                    report = f"❌ **সাবধান! এটি একটি ক্ষতিকর লিঙ্ক।**\n⚠️ **ভাইরাস পাওয়া গেছে:** `{malicious}`"
                else:
                    report = f"✅ **অভিনন্দন! এই লিঙ্কটি সম্পূর্ণ নিরাপদ।**"
                
                await msg.edit_text(report + f"\n\n👨‍💻 **Developer:** {DEVELOPER}", parse_mode='Markdown')
            else:
                await msg.edit_text("❌ **API লিমিট শেষ অথবা ভুল লিঙ্ক।**")
        except Exception as e:
            await msg.edit_text(f"⚠️ **ভুল হয়েছে:** `{str(e)}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ **অনুগ্রহ করে একটি সঠিক লিঙ্ক (URL) পাঠান।**", parse_mode='Markdown')

# --- ৪. মেইন ফাংশন ---
def main():
    # বটকে জাগিয়ে রাখার সার্ভার চালু করা
    keep_alive()
    
    # টেলিগ্রাম বট সেটআপ
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 AX Virus Scanner is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
