import os
import discord
from discord.ext import commands, tasks
from facebook_scraper import get_posts, get_photos, set_user_agent

intents = discord.Intents.default()

client = commands.Bot(command_prefix="!", intents=intents)
facebook_profile_url = "babkaankalenanna"
channel_ids = {827552957951901716: 827552957951901720}
last_posts = []

client.description = "prefix: anna"

set_user_agent("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")

@client.event
async def on_ready():
    fetch_posts()
    if not send_new_photos.is_running():
        send_new_photos.start()
    print(f"Logged in as {client.user}! posting to {channel_ids}")

@tasks.loop(seconds=0, minutes=15, hours=0, count=None)
async def send_new_photos():
    if not channel_ids:
        return
    print("task started")    
    new_photos = fetch_posts()
    print(new_photos)
    for guild_id, channel_id in channel_ids.items():
        guild = client.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        for photo in new_photos:
            await channel.send(photo)

def fetch_posts():
    new_photos = []
    for post in get_posts(facebook_profile_url, pages=3):
        if 'image' in post:
            if post['image'] not in last_posts:
                last_posts.append(post['image'])
                new_photos.append(post['image'])
    return new_photos


@client.command()
async def setchannel(ctx):
    await ctx.send("Please mention the channel where you want to post the photos.")
    try:
        msg = await client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
        channel_id = int(msg.content.replace("<#", "").replace(">", ""))
    except Exception:
        await ctx.send("Invalid channel selected.")
        return

    channel_ids[ctx.guild.id] = channel_id
    print(channel_ids)
    await ctx.send(f"Photos will now be posted in <#{channel_ids[ctx.guild.id]}>.")

@client.command()
async def cat(ctx):
    await ctx.send('meow')

client.run(os.environ.get("TOKEN"))
