import discord
from discord.ext import commands , tasks 
from itertools import cycle
import openai
import os
from asyncio import sleep
import requests
import json

with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.dm_typing=True
intents.dm_messages = True


bot = commands.Bot(command_prefix='+' , intents=intents, status=discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.watching, name="DM's"))

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.command()
async def creator(ctx):
    await ctx.send('<@791330543479685131>')
@bot.command()
async def list(ctx):
    await ctx.send('`Unable to run the commands . Try later.`')
@bot.command()
async def Hello(ctx):
    await ctx.send('Hey!')

@bot.command()
async def echo(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
# @commands.has_permissions(administrator=True)
async def join(ctx):
    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    # Get the voice channel of the user
    voice_channel = ctx.author.voice.channel

    # Connect to the voice channel
    await voice_channel.connect()
    # await ctx.send(f"Joined {voice_channel}.")
    await ctx.message.add_reaction('👍')
@bot.command()
# @commands.has_permissions(administrator=True)
async def leave(ctx):
    # Check if bot is in a voice channel
    if not ctx.voice_client:
        await ctx.send("I am not connected to a voice channel.")
        return

    # Disconnect from the voice channel
    await ctx.voice_client.disconnect()
    # await ctx.send("Left voice channel.")
    await ctx.message.add_reaction('👋')
@bot.command()
async def vote(ctx, *, question: str):
    # Delete the command message to make the channel look cleaner
    await ctx.message.delete()

    # Create the poll message with the question
    poll_embed = discord.Embed(title=f"{question}", color=0x00ff00)
    # poll_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    # Add the reactions to the poll message
    poll_message = await ctx.send(embed=poll_embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

@bot.command()
async def embed(ctx, *, question: str):
    # Delete the command message to make the channel look cleaner
    await ctx.message.delete()

    # Create the poll message with the question
    poll_embed = discord.Embed(title=f"{question}", color=0x00ff00)
    poll_message = await ctx.send(embed=poll_embed)

birthdays = {}

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def birthday(ctx, date, *, message):
    """Set your birthday and the message to be sent on that day"""
    try:
        date_obj = discord.utils.parse_time(date)
        if not date_obj:
            raise ValueError
        if date_obj not in birthdays:
            birthdays[date_obj] = []
        birthdays[date_obj].append((ctx.author.id, message))
        await ctx.send(f"Your birthday has been set to {date} and your message is {message}.")
    except ValueError:
        await ctx.send("Please provide a valid date in ISO 8601 format (e.g. YYYY-MM-DD).")

@bot.event
async def on_member_join(member):
    """Check if a member's birthday is today and give them the birthday role"""
    today = discord.utils.utcnow().date()
    if today in birthdays:
        for user_id, message in birthdays[today]:
            if member.id == user_id:
                role = discord.utils.get(member.guild.roles, name="Birthday")
                await member.add_roles(role)
                await member.send(f"Happy birthday, {member.name}! {message}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def timeout(ctx, member: discord.Member, time: int, *, reason=None):
    """Timeout a member for a specified amount of time"""
    timeout_role = discord.utils.get(ctx.guild.roles, name='Timeout')

    if not timeout_role:
        timeout_role = await ctx.guild.create_role(name='Timeout')

        for channel in ctx.guild.channels:
            await channel.set_permissions(timeout_role, send_messages=False)

    await member.add_roles(timeout_role, reason=reason)
    await ctx.send(f"{member.mention} has been timed out for {time} seconds. Reason: {reason}")

    await sleep(time)

    await member.remove_roles(timeout_role, reason="Timeout expired")
    await ctx.send(f"{member.mention} has been untimed out.")

@bot.command()
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"{amount} message(s) have been purged.")
    

# @bot.event
# async def on_message(message):
#     # if message.author == bot.user:
#     #     return 

#     if isinstance(message.channel, discord.DMChannel):
#         user = message.author
#         await message.channel.send("Your dm has been forwarded")

@bot.command()
@commands.has_permissions(administrator=True)
async def giverole(ctx, role_id: int, member: discord.Member = None):
    role = ctx.guild.get_role(role_id)

    if member is None:
        member = ctx.author

    await member.add_roles(role)
    await ctx.send(f"{member.mention} has been given the {role.name} role.")


@bot.command()
@commands.has_permissions(administrator=True)
async def removerole(ctx, role_id: int, member: discord.Member = None):
    role = ctx.guild.get_role(role_id)

    if member is None:
        member = ctx.author

    await member.remove_roles(role)
    await ctx.send(f"{role.name} role has been removed from `{member.mention}`.")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked from the server.")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned from the server.")
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == member:
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} has been unbanned from the server.")
            return

    # If the execution reaches this point, the user was not found in the banned list
    await ctx.send(f"{member} was not found in the banned list.")





@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):  # If the message is from a DM channel
        channel = bot.get_channel(1081630592661213285)  # Replace YOUR_CHANNEL_ID with the ID of the target channel
        author = message.author.name
        content = message.content


        try:
            await channel.send(f"**{author}** said: {content}")  # Forward the message to the target channel
        except Exception as e:
            print(f"Error sending message: {e}")


    await bot.process_commands(message)  # Process other commands and events as usual


@bot.command()
async def waifu(ctx):
    waifu = requests.get("https://api.waifu.pics/sfw/waifu")
    waifu2= waifu.json()
    await ctx.send(waifu2["url"])
@bot.command()
async def cuddle(ctx):
    cuddle = requests.get("https://api.waifu.pics/sfw/cuddle")
    cuddle2= cuddle.json()
    await ctx.send(cuddle2["url"])
@bot.command()
async def hug(ctx):
    hug = requests.get("https://api.waifu.pics/sfw/hug")
    hug2= hug.json()
    await ctx.send(hug2["url"])
@bot.command()
async def kiss(ctx):
    kiss = requests.get("https://api.waifu.pics/sfw/kiss")
    kiss2= kiss.json()
    await ctx.send(kiss2["url"])
@bot.command()
async def bully(ctx):
    bully = requests.get("https://api.waifu.pics/sfw/bully")
    bully2= bully.json()
    await ctx.send(bully2["url"])
@bot.command()
async def cringe(ctx):
    cringe = requests.get("https://api.waifu.pics/sfw/bully")
    cringe2= cringe.json()
    await ctx.send(cringe2["url"])

@bot.command()
async def kill(ctx):
    kill = requests.get("https://api.waifu.pics/sfw/kill")
    kill2= kill.json()
    await ctx.send(kill2["url"])
@bot.command()
async def nom(ctx):
    nom = requests.get("https://api.waifu.pics/sfw/kiss")
    nom2= nom.json()
    await ctx.send(nom2["url"])

@bot.command()
async def handhold(ctx):
    handhold = requests.get("https://api.waifu.pics/sfw/handhold")
    handhold2= handhold.json()
    await ctx.send(handhold2["url"])


# @bot.command()
# @commands.has_permissions(administrator=True)
# async def neko(ctx):
#     neko = requests.get("https://api.waifu.pics/nsfw/neko")
#     neko2= neko.json()
#     await ctx.send(neko2["url"])


# @bot.command()
# @commands.has_permissions(administrator=True)
# async def trap(ctx):
#     trap = requests.get("https://api.waifu.pics/nsfw/trap")
#     trap2= trap.json()
#     await ctx.send(trap2["url"])


# @bot.command()
# @commands.has_permissions(administrator=True)
# async def wyfu(ctx):
#     wyfu = requests.get("https://api.waifu.pics/nsfw/waifu")
#     wyfu2= wyfu.json()
#     await ctx.send(wyfu2["url"])



bot.run('')
