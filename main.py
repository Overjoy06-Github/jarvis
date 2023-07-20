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
@client.command(name='character_info',aliases=['aa', 'char_info', 'Aa'], help='Fetch information about an Anime Adventures character.')
async def character_info(ctx, *, character_name):
    character = character_name.title().replace(" ", "_")
    print(f"User's message: {character_name}")
    try:
        html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
        soup = BeautifulSoup(html_text, 'html.parser')

        #character name | Metal Knight (Bofoi)
        character_name = soup.find('h1', class_='page-header__title')
        character_name = ' '.join(character_name.stripped_strings)

        #character evolution name | Metal Knight (Arsenal)
        character_div = soup.find('div', class_='mobile-hidden')
        character_evolution_name = character_div.text.strip()

        #description | Metal Knight  is a Mythical unit based on Metal Knight, from the anime One Punch Man. He is only obtainable through summons, and requires 5k kills to evolve.
        description = soup.find('div', class_='mw-parser-output').find('p')
        extracted_text = soup.find('p').text.strip()
        modified_text = extracted_text.replace("MythicalMythical", "Mythical")

        # images | non_shiny_image | shiny_image
        figures = soup.select('section.pi-item.pi-panel.pi-border-color.wds-tabber figure')
        non_shiny_image = None
        shiny_image = None
        for i, figure in enumerate(figures):
            image_url = figure.find('img', class_='pi-image-thumbnail')['src']

            if i == 0:
                non_shiny_image = image_url
            elif i == 1:
                shiny_image = image_url

        captions = soup.find_all('figcaption', class_='pi-item-spacing pi-caption')
        caption1 = captions[0].get_text(strip=True)
        caption2 = captions[1].get_text(strip=True)

        #formatted_materials_str
        required_items_row = soup.select('table.article-table tr')[0]
        td_elements = required_items_row.find_all('td')
        materials = td_elements[1].get_text(strip=False).replace('Required Items:', '').replace('\n', '').split('x')
        materials = [material.strip() for material in materials if material.strip()]
        def format_material(material):
            return f"{material[0]}x {material[1]}"

        formatted_materials = [format_material(material.split(maxsplit=1)) for material in materials]
        formatted_materials_str = '\n'.join(formatted_materials)

        '''
        response = f"**Character Name:** {character_name}\n" \ ✅
                   f"**Description:** {modified_text}\n" \ ✅
                   f"**Character Evolution:** {character_evolution_name}\n" \ ✅
                   f"**Formatted Materials:**\n{formatted_materials_str}\n" \
                   f"**Non-Shiny Image:** {non_shiny_image}\n" \
                   f"**Shiny Image:** {shiny_image}"
        '''
        embed = discord.Embed(title=character_name,description=modified_text,color=discord.Color.blue())
        embed.add_field(name="**Materials:**", value=formatted_materials_str, inline=False)
        embed.add_field(name="**Results:**", value=character_evolution_name, inline=True)
        embed.add_field(name="**Normal Version:**", value="*"+caption1+"*", inline=False)
        embed.set_image(url=non_shiny_image)
        embed.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")
        embed.url = f"https://animeadventures.fandom.com/wiki/{character_name}"
        embedVar = discord.Embed(description="**Shiny Version:**\n*"+caption2+"*",color=discord.Color.blue())
        embedVar.set_image(url=shiny_image)
        embedVar.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")

        await ctx.send(embed=embed)
        await ctx.send(embed=embedVar)

    except Exception as e:
        print(f"Error fetching information for {character_name}: {e}")
        await ctx.send("Character not found or error occurred while fetching information.")

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
