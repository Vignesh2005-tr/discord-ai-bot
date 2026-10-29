import os
import discord
from discord.ext import commands
from google import genai
from flask import Flask
from threading import Thread

# --- WEB SERVER (KEEPS BOT AWAKE) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is awake and running!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- BOT CONFIGURATION ---
# We use os.getenv so keys remain hidden in the cloud settings
DISCORD_TOKEN = os.getenv("MTU2NTAxNDI1NTk1NzE4MDU1Nw.G1dzpZ.39AANiOKBMlNMTWbmI-jXIa_g9yMRsdhszZyPQ")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6JtCqSAfb80JD-hGEfp4HVezpUllFFnTWCOK3fTXe-apA")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} (ID: {bot.user.id})")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        user_prompt = message.clean_content.replace(f"@{bot.user.name}", "").strip()

        if not user_prompt:
            await message.reply("Hello! Ask me any question.")
            return

        async with message.channel.typing():
            try:
                response = ai_client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=user_prompt,
                )
                reply_text = response.text

                if len(reply_text) > 2000:
                    for i in range(0, len(reply_text), 1900):
                        await message.reply(reply_text[i:i + 1900])
                else:
                    await message.reply(reply_text)

            except Exception as e:
                await message.reply(f"Error: {e}")

    await bot.process_commands(message)

# --- RUN EVERYTHING ---
keep_alive()
bot.run(DISCORD_TOKEN)