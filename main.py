import discord
import requests
from copy import copy
from discord import Forbidden
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import openai
import json
import os
from asyncio import sleep
from colorama import Fore, Back, Style
import random

activity = discord.Game(name="/help")
creators = ["YOUR_ID_HERE"]
sudoers = creators #/sudo @user command

def get_prefix(client, message):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)

  return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix,
                      intents=discord.Intents.all(),
                      case_insensitive=True,
                      activity=activity,
                      status=discord.Status.online)




@client.command()
async def MEGAPING(ctx, user: discord.Member, pings,* , message=""):
  if str(ctx.author.id) in creators:
    pings_finished = 0
  while pings_finished < int(pings):
    await ctx.send(user.mention + message, delete_after=0)
    await ctx.send(user.mention + message, delete_after=0)
    await ctx.send(user.mention + message, delete_after=0)
    pings_finished += 3
    await sleep(0.5)


@client.command(name="Lie?")
async def lie_detector(ctx, *, message):
  random_number = random.randint(1,2)
  if random_number == 1:
    await ctx.reply("LIE!")
  elif random_number == 2:
    await ctx.reply("TRUTH!")
  else:
    await ctx.reply("My code is broken :(")
  

@client.command()
async def guilds(ctx):
  if str(ctx.author.id) in creators:
    await ctx.author.send(client.guilds)


@client.command(hidden=True)
async def sudo(ctx, victim: discord.Member, *, command):
  if str(ctx.author.id) in sudoers:
    """Take control."""
    new_message = copy(ctx.message)
    new_message.author = victim
    new_message.content = ctx.prefix + command
    await client.process_commands(new_message)


@client.event
async def on_guild_join(guild):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)

  prefixes[str(guild.id)] = "/"

  with open('prefixes.json', 'w') as f:
    json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
  with open('prefixes.json', 'r') as f:
    prefixes = json.load(f)

  prefixes.pop(str(guild.id))


@client.command()
async def prefix(ctx,*, prefix=""):
  if ctx.message.author.guild_permissions.administrator or str(ctx.message.author.id) in creators:
      if prefix == "":
        await ctx.reply("The prefix cannot be blank!")
      else:
        with open('prefixes.json', 'r') as f:
          prefixes = json.load(f)
  
        prefixes[str(ctx.guild.id)] = str(prefix)
  
        with open('prefixes.json', 'w') as f:
          json.dump(prefixes, f, indent=4)
  
        await ctx.reply(f"The server prefix is now {prefix}")
  else:
    await ctx.reply("You don't have permission to change the prefix")


@client.command()
async def protocol(ctx, protocol, guild):
  if str(ctx.author.id) in creators:
    if protocol == "2465":
      guild = guild or ctx.guild.id
      await client.get_guild(int(guild)).leave()
      print(client.guilds)
    if protocol == "24":
      guild = client.get_guild(int(guild))
      channel = guild.text_channels[0]
      invitelink = await channel.create_invite(max_uses=1)
      await ctx.author.send(f"{client.get_user(int(guild.owner.id))} | {invitelink}")


@client.command()
async def chat_protocol(ctx, protocol, channel, *, message):
  if str(ctx.author.id) in creators:
    if protocol == "2163":
      channel = client.get_channel(int(channel))
      await channel.send(f"{message}")
    if protocol == "2164":
      user = await client.fetch_user(str(channel))
      await user.send(str(message))
      await ctx.author.send(f"Message sent to {user.name}\n\n {message}")

@client.event
async def on_ready():
  await client.wait_until_ready()
  print(f"{client.guilds}")
  print("Connected!")
  # send embed to creators
  for ID in creators:
    user = await client.fetch_user(ID)
    hi_user_english = f"Hi, {user.name}\n"
    hi_user_tagalog = get_response(
      f"Translate The Word Hi, {user.name} in tagalog") + "\n"
    hi_user_spanish = get_response(
      f"Translate The Word Hi, {user.name} in spanish") + "\n"
    bot_online_english = "Bot online!\n"
    bot_online_tagalog = "Ang bot ay online na\n"
    bot_online_spanish = get_response(
      "Translate The Word Bot online! in spanish") + "\n"
    embed = discord.Embed(
      title=f"*** ***{hi_user_english} {hi_user_tagalog}{hi_user_spanish}",
      description=
      f"{bot_online_english}{bot_online_tagalog}{bot_online_spanish}")
    await user.send("", embed=embed)


def get_response(question):
  openai.api_key = os.getenv("KEY")
  response = openai.Completion.create(model="text-davinci-003",
                                      prompt=f"\nQ:{question}\nA:",
                                      temperature=0,
                                      max_tokens=250,
                                      top_p=1,
                                      frequency_penalty=0,
                                      presence_penalty=0)
  response = {response['choices'][0]['text']}
  return str(response).replace("{'", '').replace("'}", '').replace(
    '{"', '').replace('"}', '').replace("\n", "\\n") + "\n".replace(
      "\n\n", "\\n\\n") + "\n" + "\n"


@client.command(name="AI", description="Talk with an AI")
async def AI(ctx, *, prompt=""):
    global prev_prompt
    # Set the previous prompt as the current prompt
    # Use the OpenAI API to generate a response
    if prev_prompt=="":
      ai_response = get_response(f"{prompt}")
    else:
      ai_response = get_response(f"Previous prompt: {prev_prompt}, {prompt}")
    prev_prompt = prompt
    # Send the response to the channel
    await ctx.send(ai_response)

@client.command()
async def prev_prompt(ctx):
    global prev_prompt
    # Send the previous prompt to the channel
    await ctx.send(prev_prompt)


@client.command(name="translate",
                description="Translate a Word",
                aliases=["translator"])
async def translate(ctx, Language_to_translate_into, *, message_to_translate):
  await ctx.reply(
    get_response(
      f"Translate The Word {message_to_translate} in {Language_to_translate_into}"
    ))


@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.content.lower(
  ) == "<@1062349998639034509>prefix" or message.content.lower(
  ) == "@IronAI#5065prefix" or message.content.lower(
  ) == "@IronAI#5065 prefix" or message.content.lower(
  ) == "<@1062349998639034509> prefix":
    with open('prefixes.json', 'r') as f:
      prefixes = json.load(f)

    await message.reply(
      f"The server prefix is {prefixes[str(message.guild.id)]}")
  if f"{message.author.id}_deleted?" in db.keys():
    if db[f"{message.author.id}_deleted?"] == True:
      await message.delete()
    


@client.command()
async def history(ctx):
  text_channel_list = []
  embed_description = ""

  for server in client.guilds:
    for channel in server.channels:
      if str(channel.type) == 'text':
        text_channel_list.append(channel.id)

  else:
    for item in text_channel_list:
      channel = client.get_channel(item)
      print(
        f"working on channel {text_channel_list.index(item) + 1}/{len(text_channel_list)} (#{channel.name} id: {item}"
      )
      messages = 0
      try:
        async for _ in channel.history(limit=None):
          messages += 1
        else:
          async for msg in channel.history(limit=messages):
            if str(msg.content).lower().startswith("/ai"):
              if ctx.author == msg.author:
                if msg.content != "" or msg.content != " " or msg.content != "*** ***" or msg.content != "":
                  embed_description += msg.content.replace('/ai', '') + '\n'
      except Forbidden:
        print(
          f"I dont have access to channel {text_channel_list.index(item) + 1}/{len(text_channel_list)}"
        )
    else:
      print("All channels scanned")
      print(embed_description)
      history_embed = discord.Embed(title="AI PROMPTS",
                                    description=f"**{embed_description}**")
      await ctx.author.send("", embed=history_embed)



@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send(error, delete_after=5)
    await ctx.message.delete()
    print(f"{Fore.RED}ERROR: \n")
    print(f"{Fore.RED}{error}{Fore.WHITE}")
  else:
    await ctx.send(error)
    print(f"{Fore.RED}error: \n")
    print(f"{Fore.RED}{error}{Fore.WHITE}")


if __name__ == "__main__":
  cogs = ["sudo"]
  for cog in cogs:
    client.load_extension(cog)


client.remove_command('help')

@client.command(name="help")
async def help(ctx):
  help_embed = discord.Embed(title=f"{client.user} | Help",description="""
    AI - Talk with an AI
    Lie? - Lie detector
    history - shows your history
    prefix - set prefix
    nick - set nick
    prev_prompt - shows previous prompt across all servers by every user
    help - shows this message
""", colour=discord.Colour.blue())
  help_embed.set_footer(text=' Bot Made by ScriptGuild Team\nBot Developed by\n\nKentcaps#5290\nRGB CAT#0001')
  await ctx.send(embed=help_embed)

client.run(os.getenv("TOKEN"))
