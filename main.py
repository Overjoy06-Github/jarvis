import discord
from discord.ext import commands
import os
from discord import Spotify
from bs4 import BeautifulSoup
import requests
from anime_adventures import *
import random
from custom_emojis import custom_emojis
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv("TOKEN")
client = commands.Bot(command_prefix='Jarvis ', description="Test Bot", intents=intents)
ANILIST_BASE_URL = 'https://graphql.anilist.co'

# prints when the bot is running/online
@client.event
async def on_ready():
    print(f'{client.user.name} is now running.')

# dictionary
evolution_mappings = {
    'Akeno evo': 'Akena (Fallen Angel)',
    'Akena evo': 'Akena (Fallen Angel)'
}

# anime command
@client.command(name='anime', help='Fetch information about any anime.')
async def fetch_anime_info(ctx, *, anime_name):
    def get_anime_info(anime_name):
        query = '''
        query ($search: String) {
            Media(search: $search, type: ANIME) {
                title {
                    english
                }
                episodes
                averageScore
                description
                coverImage {
                    large
                }
            }
        }
        '''

        variables = {
            'search': anime_name
        }

        # Make a request to the AniList API to get anime details
        response = requests.post(ANILIST_BASE_URL, json={'query': query, 'variables': variables})
        data = response.json()

        if 'data' in data and data['data']['Media']:
            anime = data['data']['Media']
            title = anime['title']['english'] or anime_name
            episodes = anime['episodes']
            score = anime['averageScore']
            synopsis = anime['description']
            image_url = anime['coverImage']['large']

            anime_info = {
                'title': title,
                'episodes': episodes,
                'score': score,
                'synopsis': synopsis,
                'image_url': image_url
            }

            return anime_info
        else:
            return None

    anime_info = get_anime_info(anime_name)
    if anime_info:
        title = anime_info['title']
        episodes = anime_info['episodes']
        score = anime_info['score']
        synopsis = anime_info['synopsis']
        image_url = anime_info['image_url']

        embed = discord.Embed(title=title, description=synopsis, color=discord.Color.blue())
        embed.add_field(name="**Episodes:**", value=episodes, inline=False)
        embed.add_field(name="**Score:**", value=score, inline=False)
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Anime '{anime_name}' not found.")

# Web scraping for animeadventures.fandom.com
@client.command(name='character_info',aliases=['aa', 'char_info', 'Aa'], help='Fetch information about an Anime Adventures character.')
async def character_info(ctx, *, character_name):
    original_character_name = character_name  # Store the original input for later use
    print(original_character_name)
    character_name_lower = character_name.lower()
    for key in evolution_mappings.keys():
        if character_name_lower == key:
            character_name = evolution_mappings[key]
            break

    character = character_name.title().replace(" ", "_")
    print(f"User's message: {character_name}")
    try:
        html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
        soup = BeautifulSoup(html_text, 'html.parser')

        #character name | Metal Knight (Bofoi)
        character_name_elem = soup.find('h1', class_='page-header__title')
        if character_name_elem:
            character_name = ' '.join(character_name_elem.stripped_strings)

        #character evolution name | Metal Knight (Arsenal)
        character_div = soup.find('div', class_='mobile-hidden')
        if character_div:
            character_evolution_name = character_div.text.strip()
        else:
            character_evolution_name = "Evolution name not available."

        #description | Metal Knight  is a Mythical unit based on Metal Knight, from the anime One Punch Man. He is only obtainable through summons, and requires 5k kills to evolve.
        description_elem = soup.find('div', class_='mw-parser-output').find('p')
        if description_elem:
            extracted_text = description_elem.text.strip()
            modified_text = extracted_text.replace("MythicalMythical", "Mythical")
        else:
            modified_text = "Description not available."

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
        caption1 = captions[0].get_text(strip=True) if captions else "..."
        if len(captions) > 1:
            caption2 = captions[1].get_text(strip=True)
        else:
            caption2 = caption1


        def format_material(material):
            quantity, item = material
            item = item.strip()

            if item.startswith("Star Fruit"):
                base_item = "StarFruit"
                if item in custom_emojis:
                    emoji_id = custom_emojis[item]
                    emoji_name = base_item + "".join([word.capitalize().replace('(', '_').replace(')', '').replace("'", "") for word in item.split()[2:]])
                    return f"{quantity}x {item} <:{emoji_name}:{emoji_id}>"

            if item in custom_emojis:
                emoji_id = custom_emojis[item]
                emoji_name = item.replace(' ', '_').replace("'", "") 
                return f"{quantity}x {item} <:{emoji_name}:{emoji_id}>"
            else:
                return f"{quantity}x {item}"
    
        required_items_row = soup.select('table.article-table tr')[0]
        td_elements = required_items_row.find_all('td')
        materials = td_elements[1].get_text(strip=False).replace('Required Items:', '').replace('\n', '').split('x')
        materials = [material.strip() for material in materials if material.strip()]

        formatted_materials = [format_material(material.split(maxsplit=1)) for material in materials]
        formatted_materials_str = '\n'.join(formatted_materials)

        embed = discord.Embed(title=character_name,description=modified_text,color=discord.Color.blue())
        embed.add_field(name="**Materials:**", value=formatted_materials_str, inline=False)
        embed.add_field(name="**Results:**", value=character_evolution_name, inline=False)
        embed.add_field(name="**Normal Version:**", value="*"+caption1+"*", inline=True)
        embed.set_image(url=non_shiny_image)
        embed.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")
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
