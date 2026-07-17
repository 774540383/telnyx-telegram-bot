import os
import requests
import telnyx

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = FastAPI()

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_NUMBER = os.getenv("TELNYX_NUMBER")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

telnyx.api_key = TELNYX_API_KEY


# -----------------------
# Telegram
# -----------------------

telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☎️ Telnyx Bot Ready\n\n"
        "/call الرقم\n"
        "/sms الرقم الرسالة\n"
        "/status"
    )


async def call(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 1:
        await update.message.reply_text(
            "استخدم:\n/call +967xxxxxxxxx"
        )
        return

    number = context.args[0]

    try:

        call = telnyx.Call.create(
            connection_id=os.getenv(
                "TELNYX_CONNECTION_ID"
            ),
            to=number,
            from_=TELNYX_NUMBER
        )

        await update.message.reply_text(
            f"✅ تم بدء الاتصال\n{number}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"خطأ: {e}"
        )


async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        await update.message.reply_text(
            "/sms الرقم الرسالة"
        )
        return

    number = context.args[0]
    message = " ".join(context.args[1:])


    try:

        telnyx.Message.create(
            from_=TELNYX_NUMBER,
            to=number,
            text=message
        )

        await update.message.reply_text(
            "✅ تم إرسال الرسالة"
        )

    except Exception as e:
        await update.message.reply_text(
            str(e)
        )


async def status(update: Update, context):
    await update.message.reply_text(
        "🟢 النظام يعمل\n"
        "Telnyx Connected"
    )



telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("call", call)
)

telegram_app.add_handler(
    CommandHandler("sms", sms)
)

telegram_app.add_handler(
    CommandHandler("status", status)
)



# -----------------------
# Telnyx Webhooks
# -----------------------


@app.post("/telnyx/voice")
async def voice(request: Request):

    data = await request.json()

    event = data.get(
        "data",
        {}
    ).get(
        "event_type"
    )


    if event == "call.initiated":

        return {
            "commands":[
                {
                    "command":
                    "speak",
                    "payload":
                    {
                        "voice":
                        "female",
                        "language":
                        "ar-SA",
                        "text":
                        "مرحبا بك"
                    }
                }
            ]
        }


    return {
        "received":True
    }



@app.post("/telnyx/sms")
async def sms_webhook(request: Request):

    data = await request.json()

    message = data["data"]["payload"]

    text = (
        "📩 رسالة جديدة\n\n"
        f"من: {message.get('from')}\n"
        f"{message.get('text')}"
    )

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id":ADMIN_CHAT_ID,
            "text":text
        }
    )


    return {
        "ok":True
    }



@app.on_event("startup")
async def startup():

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
