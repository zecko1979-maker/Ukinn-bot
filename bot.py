import asyncio, os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import AsyncOpenAI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)
async def ask_model(m,q):
    try:
        r = await client.chat.completions.create(model=m, messages=[{"role":"user","content":q}], max_tokens=600)
        return {"model":m, "ans": r.choices[0].message.content}
    except Exception as e:
        return {"model":m, "ans": f"خطأ {e}"}
async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    await update.message.reply_text("🏛️ مجلس أوكين يجتمع...")
    results = await asyncio.gather(ask_model("openai/gpt-4o-mini",q), ask_model("google/gemini-flash-1.5",q))
    all_ans = "\n\n".join([f"{r['model']}: {r['ans']}" for r in results])
    prompt = f"انت رئيس مجلس أوكين مصري. السؤال: {q} الردود: {all_ans} طلع حكم نهائي بالمصري + ميزان حقيقة"
    final = await client.chat.completions.create(model="openai/gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    await update.message.reply_text(final.choices[0].message.content[:4000])
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
