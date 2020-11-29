#bot

import os, discord, random, asyncio, datetime

from discord import Activity, ActivityType
from discord.ext import commands, tasks, timers
from datetime import datetime
from itertools import cycle
from dotenv import load_dotenv

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '!', intents = intents)
client.timer_manager = timers.TimerManager(client)
client.remove_command('help')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

statuses = open('statuses.txt').read().splitlines()
status = cycle(statuses)

#for ready
@client.event
async def on_ready():
    change_status.start()
    print(f'{client.user} is Ready!')

@tasks.loop(seconds=60)
async def change_status():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=next(status)))

#for member joining
@client.event
async def on_member_join(member):
    await member.create_dm()
    print(f'{member} has joined the Server.')
    await member.dm_channel.send(f'Hi {member.name}, Welcome to the Discord server!')

#for member leaving
@client.event
async def on_member_remove(member):
    print(f'{member} has left the Server.')

#for mentions
@client.event
async def on_message(message):
    for x in message.mentions:
        if(x==client.user):
            await message.channel.send(f":sauropod: Did someone mention me?")
    await client.process_commands(message)

#timer
@client.event
async def time_check():
    await client.wait_until_ready()
    guild = discord.utils.get(client.guilds, name='Testing')
    if guild is not None:
        channel = discord.utils.get(guild.text_channels, name='general')
    intern = discord.utils.get(client.guilds[0].roles, name='Intern')
    interns = []
    for member in client.get_all_members():
        roles = member.roles
        for role in roles:
            if role == intern:
                interns.append(member.id)
                break
    while True:
        now=datetime.strftime(datetime.now(),'%H:%M')
        time=now.split(':')
        if time[0] == '14' and time[1] == '26':
            message= "OK Interns, share your work"
            names = ""
            for user in interns:
                names = names + ' <@'+str(user)+'>'
            await channel.send(message + names)
            time=85800
        else:
            time=25
        await asyncio.sleep(time)
client.loop.create_task(time_check())

#error detection for invalid command
@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command Not Found')

#ping
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

#8ball
@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = open('responses-8ball.txt').read().splitlines()
    random.seed(a=None)
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

#error handling for 8ball
@_8ball.error
async def _8ball_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please Enter the Question')

#clear
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount+1)

#kick
@client.command()
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

#ban
@client.command()
@commands.has_permissions(manage_messages=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

#unban
@client.command()
@commands.has_permissions(manage_messages=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator =  member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if((user.name, user.discriminator)==(member_name, member_discriminator)):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

#Answers with a random quote
@client.command()
async def quote(ctx):
    quotes = open('quotes.txt').read().splitlines()
    random.seed(a=None)
    quote = random.choice(quotes)
    await ctx.send(quote)

#Embeded help with list and details of commands
@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name='Help : List of commands available for everyone')
    embed.add_field(name='!ping', value='Returns bot respond time in milliseconds', inline=False)
    embed.add_field(name='!8ball', value='Get random replies', inline=False)
    embed.add_field(name='!quote', value='Get inspired by a powerful quote', inline=False)
    embed.add_field(name='For the Admin', value='-----------------', inline=True)
    embed.add_field(name='!clear <number>', value='Deletes the specified number of messages', inline=False)
    embed.add_field(name='!Kick <username>', value='Kicks the User off the server', inline=False)
    embed.add_field(name='!Ban <username>', value='Bans the User', inline=False)
    embed.add_field(name='!Unban <username>', value='Unbans the USer', inline=False)
    await ctx.send(embed=embed)

client.run(TOKEN)
