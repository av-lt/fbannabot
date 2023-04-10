import os
import discord
from discord.ext import commands, tasks
from facebook_scraper import get_posts

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="Anna ", intents=intents)
facebook_profile_url = "https://www.facebook.com/babkaankalenanna/"
channel_ids = {}
last_fb_id = None

@client.event
async def on_ready():
    send_new_photos.start()
    print(f"Logged in as {client.user}! posting to {channel_ids}")

@tasks.loop(minutes=15)
async def send_new_photos():
    if not channel_ids:
        return
    
    new_photos = get_new_photos()
    for _, channel_id in channel_ids:
        channel = client.get_channel(channel_id)
        for photo in new_photos:
            await channel.send(photo)

def get_new_photos():
    facebook_posts = get_posts(facebook_profile_url, pages=3)

    photo_urls = []
    for post in facebook_posts:
        if post["post_id"] == last_fb_id:
            break
        if post["image"]:
            print(post["image"])
            photo_urls.append((post["image"], post["post_id"]))

    if photo_urls:
        last_fb_id = photo_urls[0][1]

    return [i[0] for i in photo_urls]

@client.command(name="setchannel")
async def set_channel(ctx):
    await ctx.send("Please mention the channel where you want to post the photos.")
    try:
        msg = await client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
        channel_id = int(msg.content.replace("<#", "").replace(">", ""))
    except Exception:
        await ctx.send("Invalid channel selected.")
        return

    channel_ids[ctx.guild.id] = channel_id
    await ctx.send(f"Photos will now be posted in <#{channel_ids[ctx.guild.id]}>.")

client.run(os.getenv("TOKEN"))
