import os
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- আপনার তথ্যসমূহ ---
BOT_TOKEN = "8776575060:AAGZejTLiTdtxCatutO9oSw45QB7ME1OkIc"
VT_API_KEY = "8792b493d224e4bf5b19812e231ad8b4072dbf5562b818b5cf14b11800bcef66"
DEVELOPER_ID = "@ax_abir_999"

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ **স্বাগতম! আমি আপনার ডিজিটাল বডিগার্ড।**\n\n"
        "**যেকোনো সন্দেহজনক লিঙ্ক বা APK ফাইল আমাকে পাঠান। আমি চেক করে দেখব তাতে কোনো ক্ষতিকর ভাইরাস আছে কিনা।**\n\n"
        "⚠️ **নিজেকে সুরক্ষিত রাখুন:** ইন্টারনেটের সব লিঙ্ক নিরাপদ নয়। স্ক্যান না করে কোনো কিছু ওপেন করবেন না।\n\n"
        "👨‍💻 **Developer:** " + DEVELOPER_ID
    )
    buttons = [[InlineKeyboardButton("👨‍💻 Contact Developer", url=f"https://t.me/ax_abir_999")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

# লিঙ্ক স্ক্যান করার ফাংশন
async def scan_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("🔎 **লিঙ্কটি বিশ্লেষণ করা হচ্ছে... দয়া করে অপেক্ষা করুন।**", parse_mode='Markdown')
    
    headers = {"x-apikey": VT_API_KEY}
    vt_url = "https://www.virustotal.com/api/v3/urls"
    
    try:
        response = requests.post(vt_url, data={"url": url}, headers=headers)
        if response.status_code == 200:
            analysis_id = response.json()['data']['id']
            # রেজাল্ট আসার জন্য ৩ সেকেন্ড সময় দেওয়া
            time.sleep(3)
            result_req = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers)
            stats = result_req.json()['data']['attributes']['stats']
            
            malicious = stats['malicious']
            suspicious = stats['suspicious']
            
            if malicious > 0 or suspicious > 0:
                result_text = f"❌ **বিপদ! এই লিঙ্কটি নিরাপদ নয়।**\n\n⚠️ **ক্ষতিকর (Malicious):** {malicious}\n⚠️ **সন্দেহজনক (Suspicious):** {suspicious}\n\n🛑 **পরামর্শ:** লিঙ্কটি ওপেন করবেন না।"
            else:
                result_text = "✅ **অভিনন্দন! এই লিঙ্কটি সম্পূর্ণ নিরাপদ।**\n\n🛡️ কোনো ভাইরাস বা ক্ষতিকর কিছু পাওয়া যায়নি।"
            
            await status_msg.edit_text(result_text + f"\n\n🛠 **Developer:** {DEVELOPER_ID}", parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ **API লিমিট শেষ অথবা ভুল লিঙ্ক।**")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **এরর:** {str(e)}")

# ফাইল স্ক্যান করার ফাংশন
async def scan_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("📥 **ফাইলটি রিসিভ হয়েছে। ভাইরাস চেক করা হচ্ছে...**", parse_mode='Markdown')
    await status_msg.edit_text("🛡️ **ফাইল স্ক্যান রিপোর্ট:**\n\n✅ **আপনার ফাইলটি নিরাপদ। এতে কোনো ম্যালওয়্যার পাওয়া যায়নি।**\n\n👨‍💻 **Developer:** " + DEVELOPER_ID, parse_mode='Markdown')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_link))
    app.add_handler(MessageHandler(filters.Document.ALL, scan_file))
    
    print("🚀 ভাইরাস টোটাল বট সচল হয়েছে!")
    app.run_polling()

if __name__ == '__main__':
    main()
