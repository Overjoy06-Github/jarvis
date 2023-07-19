import discord
from discord.ext import commands
import os
from discord import Spotify
from bs4 import BeautifulSoup
import requests
from anime_adventures import *
import random

# intents because discord decided to add a shit feature
intents = discord.Intents.default()
intents = discord.Intents.all()

# some random bullshit
TOKEN = os.getenv("TOKEN")
client = commands.Bot(command_prefix='Jarvis ', description="Test Bot", intents=intents)

# prints when the bot is running/online
@client.event
async def on_ready():
    print(f'{client.user.name} is now running.')

# anime adventures command lol
@client.command(name='aa', help='Find information about Anime Adventures units.', pass_context=True, case_insensitive=True)
async def aa(ctx, *, character_name):
    character_name = character_name.title().replace(" ", "_")
    character = character_name.lower()
    print(f"User's message: {character_name}")
    html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
    soup = BeautifulSoup(html_text, 'lxml')
    error_checker = soup.find('h1', class_='page-header__title')

    if error_checker is not None:
        character_needed = error_checker.text
        character_evolution_element = soup.find('div', class_='mobile-hidden')

        if character_evolution_element is not None:
            character_evolution_name = character_evolution_element.text
            description = soup.find('div', class_='mw-parser-output').find('p').text
            description = description.replace("MythicalMythical", "Mythical")
            banner_raw = soup.find('figure', class_='pi-item pi-image').find('img').get('src')
            imgs = soup.findAll('div', class_='mw-parser-output')

            images = []
            for div in imgs:
                img_tags = div.findAll('img')
                for img in img_tags:
                    src = img['src']
                    if 'static' in src:
                        images.append(src)

            evolution_materials = soup.find('table', class_='article-table game-font-face').text
            split_text = re.split(r"(x\d+)\s*", evolution_materials)
            transformed_text = ' '.join(split_text)
            final = transformed_text.split()
            final = final[:-5]

            def listToString(s):
                str1 = " ".join(s)  # Add space between elements
                return str1

            actual_final = listToString(final)
            actual_final = re.sub(r"\bStar Fruit \b", "Star Fruit <:Star_Fruit:1131211285887987785>", actual_final, count=1)
            actual_final = re.sub(r"\bStar Fruit \(Blue\)(?!\S)",
                                  r"Star Fruit (Blue) <:Star_Fruit_Blue:1131211288454905956>", actual_final)
            actual_final = re.sub(r"\bStar Fruit \(Green\)(?!\S)",
                                  r"Star Fruit (Green) <:Star_Fruit_Green:1131211294058496081>", actual_final)
            actual_final = re.sub(r"\bStar Fruit \(Pink\)(?!\S)",
                                  r"Star Fruit (Pink) <:Star_Fruit_Pink:1131211253486989413>", actual_final)
            actual_final = re.sub(r"\bStar Fruit \(Rainbow\)(?!\S)",
                                  r"Star Fruit (Rainbow) <:Star_Fruit_Rainbow:1131211258696319016>", actual_final)
            actual_final = re.sub(r"\bStar Fruit \(Red\)(?!\S)",
                                  r"Star Fruit (Red) <:Star_Fruit_Red:1131211261602955294>", actual_final)
            actual_final = actual_final.replace("x", "\nx")

            embedVar = discord.Embed(title=character_needed, description=description, color=0x00ff00)
            embedVar.add_field(name="Materials:", value=actual_final, inline=True)
            embedVar.add_field(name="Result", value=character_evolution_name, inline=True)
            embedVar.set_thumbnail(url=images[1])
            embedVar.set_image(url=images[2])

            await ctx.send(embed=embedVar)
        else:
            await ctx.send("Character evolution name not found.")
    else:
        await ctx.send("Character not found.")

# check what the person's spotify is playing
@client.command(name='spotify', help='Find out what songs a person is listening to.')
async def spotify(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
        pass
    if user.activities:
        for activity in user.activities:
            if isinstance(activity, Spotify):
                embed = discord.Embed(
                    title = f"{user.name}'s Spotify",
                    description = "Listening to {}".format(activity.title),
                    color = 0xC902FF)
                print(embed)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Artist", value=activity.artist)
                embed.add_field(name="Album", value=activity.album)
                embed.set_footer(text="Song started at {}".format(activity.created_at.strftime("%H:%M")))
                await ctx.send(embed=embed)
                return
    await ctx.send(f'{user} is not listening to anything.', tts=True)

@client.command(name='avatar', aliases=['av', 'Avatar', 'Av'], help='Fetch avatar of a user.')
async def dp(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.message.author
    userAvatar = member.avatar.url
    await ctx.send(userAvatar)

@client.command()
async def kys(ctx):
    await ctx.send('You first.')

@client.command()
async def goodnight(ctx):
    goodnight_messages = [
    "Goodnight! Sleep tight!",
    "Sweet dreams! Goodnight!",
    "Have a peaceful sleep! Goodnight!",
    "Wishing you a restful night! Goodnight!",
    "May you wake up refreshed! Goodnight!",
    ]
    if not ctx.author.bot:
        response = random.choice(goodnight_messages)
        await ctx.send(response)


client.run(TOKEN)