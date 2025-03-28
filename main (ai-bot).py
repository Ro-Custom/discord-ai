# pip install nextcord nest_asyncio beautifulsoup4
# pip install playwright
# python -m playwright install chromium

# use it however you want, i don't care

import nest_asyncio
import asyncio
import nextcord
from nextcord.ext import commands
from playwright.sync_api import sync_playwright
import time
import re
from bs4 import BeautifulSoup

nest_asyncio.apply()

TOKEN = "BOT TOKEN HERE!" # get it on https://discord.com/developers/applications 
INTENTS = nextcord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix=">>>", intents=INTENTS) # don't forget to enable intents for the bot

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True) # if True - browser hidden, if False - browser is visible

@bot.event
async def on_ready():
    print(f"✅ {bot.user} started!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        user_question = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not user_question:
            await message.reply("❌ Please write your question after ping.")
            return

        await message.reply("⏳ I'm getting a response, please wait...")

        url = f"https://YOURLINK-HERE.netlify.app/ai.html?question={user_question}" # I recommend using NETLIFY (https://www.netlify.com/), deploy ai.html and get link

        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        page = context.new_page()
        page.goto(url)

        time.sleep(2)

        try:
            page.click('button#launch-auth-popup')
        except Exception as e:
            await message.reply(f"❌ Auth error: {e}")
            return

        max_wait_time = 60
        elapsed_time = 0
        extracted_content = None

        while elapsed_time < max_wait_time:
            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            pre_tag = soup.find("pre")

            if pre_tag:
                match = re.search(r'"content":\s*"([^"]+)"', pre_tag.text.strip())
                if match:
                    extracted_content = match.group(1)
                    break  

            time.sleep(1)
            elapsed_time += 1

        page.close()

        if extracted_content:
            await asyncio.create_task(message.reply(f"💬 {extracted_content}"))
        else:
            await message.reply("❌ Error: {e}")


async def run_bot():
    await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except RuntimeError as e:
        print(f"{e}")
