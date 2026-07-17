import os
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

app = FastAPI()

# ENV
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_NUMBER = os.getenv("TELNYX_NUMBER")
TELNYX_APPLICATION_ID = os.getenv("TELNYX_APPLICATION_ID")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


# Telegram bot
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☎️ Telnyx Bot Ready\n\n"
        "/call +رقم\n"
        "/sms +رقم رسالة\n"
        "/status"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 النظام يعمل\n"
        "Telnyx Connected"
    )


async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "استخدم:\n/call +967xxxxxxxxx"
        )
        return

    number = context.args[0]

    try:
        url = "https://api.telnyx.com/v2/calls"

        headers = {
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "connection_id": TELNYX_APPLICATION_ID,
            "from": TELNYX_NUMBER,
            "to": number
        }

        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )

        if response.status_code in [200, 201]:

            await update.message.reply_text(
                f"☎️ تم بدء الاتصال\n{number}"
            )

        else:

            await update.message.reply_text(
                "❌ خطأ Telnyx:\n"
                + response.text
            )

    except Exception as e:

        await update.message.reply_text(
            f"❌ خطأ:\n{str(e)}"
        )


async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        await update.message.reply_text(
            "استخدم:\n/sms +رقم الرسالة"
        )
        return


    number = context.args[0]
    message = " ".join(context.args[1:])


    try:

        url = "https://api.telnyx.com/v2/messages"

        headers = {
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "from": TELNYX_NUMBER,
            "to": number,
            "text": message
        }


        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )


        if response.status_code in [200,201]:

            await update.message.reply_text(
                "📩 تم إرسال الرسالة"
            )

        else:

            await update.message.reply_text(
                "❌ خطأ SMS:\n"
                + response.text
            )


    except Exception as e:

        await update.message.reply_text(
            f"❌ خطأ:\n{str(e)}"
        )



# Webhooks

@app.post("/telnyx/voice")
async def telnyx_voice(request: Request):

    data = await request.json()

    print("VOICE EVENT:")
    print(data)

    return {
        "received": True
    }



@app.post("/telnyx/sms")
async def telnyx_sms(request: Request):

    data = await request.json()

    print("SMS EVENT:")
    print(data)

    return {
        "received": True
    }



@app.get("/")
def home():

    return {
        "status": "Telnyx Telegram Bot Running"
    }



# Telegram handlers

telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("status", status)
)

telegram_app.add_handler(
    CommandHandler("call", call)
)

telegram_app.add_handler(
    CommandHandler("sms", sms)
)



@app.on_event("startup")
async def startup():

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()



@app.on_event("shutdown")
async def shutdown():

    await telegram_app.stop()
    await telegram_app.shutdown()
