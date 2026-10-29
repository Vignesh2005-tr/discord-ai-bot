import os
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask
from openai import OpenAI

# --- WEB SERVER (KEEPS BOT AWAKE) ---
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is awake and running!"


def run_server():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)


def keep_alive():
    Thread(target=run_server, daemon=True).start()


# --- BOT CONFIGURATION ---
DISCORD_TOKEN = os.getenv("MTU2NTAxNDI1NTk1NzE4MDU1Nw.G1dzpZ.39AANiOKBMlNMTWbmI-jXIa_g9yMRsdhszZyPQ")
OPENAI_API_KEY = os.getenv("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")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN environment variable.")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

# Initialize OpenAI client
ai_client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} (ID: {bot.user.id})")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        prompt = message.clean_content
        for mention in message.mentions:
            if mention.id == bot.user.id:
                prompt = prompt.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "")
                break

        prompt = prompt.strip()

        if not prompt:
            await message.reply("Hello! Ask me any question.")
            return

        async with message.channel.typing():
            try:
                response = ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                )

                reply_text = response.choices[0].message.content

                if len(reply_text) > 2000:
                    for i in range(0, len(reply_text), 1900):
                        await message.reply(reply_text[i : i + 1900])
                else:
                    await message.reply(reply_text)

            except Exception as e:
                await message.reply(f"Error: {e}")

    await bot.process_commands(message)


# --- RUN EVERYTHING ---
if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)