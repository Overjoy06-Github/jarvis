from discord.ext import commands
from anime_adventures import *
from dotenv import load_dotenv
from discord import Spotify
from characterai import PyAsyncCAI
from evolution_mappings import evolution_mappings
import traceback
import asyncio
import discord
import random
import ast
import os

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.environ['TOKEN']
client = commands.Bot(command_prefix='Jarvis ', description="Test Bot", intents=intents)
ANILIST_BASE_URL = 'https://graphql.anilist.co'
chai_token = os.environ['CHAI_TOKEN']

@client.command(name='probabilities', help='Check out the probability of any number!')
async def probabilities(ctx, percentage: float):
    if percentage <= 0 or percentage > 100:
        await ctx.send('Invalid percentage. Please provide a value between 0 and 100.')
        return
    
    chance = 1 / (percentage / 100)
    response = f'1 in {int(chance):,} chances'
    await ctx.send(response)

@client.command(name='shiny', help='Test out your luck using this command!')
async def shiny(ctx, variant: str = None):
    if variant == 'secret':
        chance = random.random()  # Generates a random number between 0 and 1
        if chance <= 0.03:  # 3% chance
            response = "You `WILL` get a shiny. | 3% Chance for a shiny secret unit if you're host, and if you have the shiny hunter gamepass."
        else:
            response = "You will `NOT` get a shiny. | 3% Chance for a shiny secret unit if you're host, and if you have the shiny hunter gamepass."
    elif variant == 'mythical':
        chance = random.random()  # Generates a random number between 0 and 1
        if chance <= 0.00015:  # 0.015% chance
            response = 'You `WILL` get a shiny mythical. | 0.015% Chance for a shiny mythical unit if you have the shiny hunter gamepass.'
        else:
            response = 'You will `NOT` get a shiny mythical. | 0.015% Chance for a shiny mythical unit if you have the shiny hunter gamepass.'
    else:
        response = 'Invalid variant. Available variants: `secret`, `mythical`'

    await ctx.send(response)

@client.command()
async def talk(ctx, *, message: str, help='Talk with Jarvis!'):
    async with asyncio.timeout(60):
        cai_client = PyAsyncCAI(chai_token)
        await cai_client.start()
        char = "1U5b4Nuuf3LnBLvAbaxUfllTYvttzWH2m4hjvj5ubfE"
        chat = await cai_client.chat.get_chat(char)
        history_id = chat["external_id"]
        participants = chat["participants"]
        print(message)

        if not participants[0]["is_human"]:
            tgt = participants[0]["user"]["username"]
        else:
            tgt = participants[1]["user"]["username"]

        try:
            data = await asyncio.wait_for(
                cai_client.chat.send_message(
                    char, message, history_external_id=history_id, tgt=tgt
                ),
                timeout=30,  # Adjust the timeout period as needed
            )
            name = data["src_char"]["participant"]["name"]
            text = data["replies"][0]["text"]

            cai_response = f"**{name}:**  `{text}`"
            print(cai_response)
            await ctx.send(cai_response)

        except asyncio.TimeoutError:
            await ctx.send("The conversation timed out.")

# prints when the bot is running/online
@client.event
async def on_ready():
    print(f'{client.user.name} is now running.')

@client.command(name='8ball', help='Ask the 8-ball a question and receive a yes or no answer!')
async def eight_ball(ctx, *, question: str):
    responses = ["Yes", "No"]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

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
    original_character_name = character_name
    print("Original Character Name:", original_character_name)
    character_name_lower = character_name.lower()
    if character_name_lower in evolution_mappings:
        character_name = evolution_mappings[character_name_lower]
    else:
        character_name = character_name.title().replace(" ", "_")

    for key in evolution_mappings.keys():
        if character_name_lower == key.lower():
            character_name = evolution_mappings[key]
            break

    print(f"User's message: {character_name}")
    formatted_materials_str = None  # Define the variable outside the try block

    try:
        html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character_name}').text
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
            if len(material) == 2:
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
            else:
                return "Invalid material format."
    
        required_items_row = soup.select('table.article-table tr')
        if required_items_row:
            td_elements = required_items_row[0].find_all('td')
            if len(td_elements) > 1:
                materials_text = td_elements[1].get_text(strip=False).replace('Required Items:', '').replace('\n', '')
                if materials_text:
                    materials = materials_text.split('x')
                    materials = [material.strip() for material in materials if material.strip()]

                    formatted_materials = [format_material(material.split(maxsplit=1)) for material in materials]
                    formatted_materials_str = '\n'.join(formatted_materials)
                else:
                    formatted_materials_str = "None"
            else:
                formatted_materials_str = "None"
        else:
            formatted_materials_str = "None"

        damage_type = soup.find_all('div', class_='pi-data-value pi-font')
        damage_type1 = damage_type[4].get_text(strip=True) if captions else "..."
        damage_type2 = damage_type[5].get_text(strip=True) if captions else "..."
        damage_type3 = damage_type[6].get_text(strip=True) if captions else "..."

        def get_custom_emoji(name):
            return f"<:{name}:{custom_emojis.get(name, '')}>"

        if damage_type3 in custom_emojis:
            damage_type3 = f"{damage_type3} {get_custom_emoji(damage_type3)}"
        else:
            damage_type3 = "..."

        damage_type2 = f"{damage_type2} {get_custom_emoji(damage_type2)}"

        special_effect_text = "Attacks 1 time in a single attack."
        special_effect_elements = soup.find_all('div', class_='mw-collapsible')

        special_effect_printed = False

        for effect in special_effect_elements:
            if effect.get('style') == 'display: none;':
                special_effect = effect.find('div', class_='game-tooltip__container game-font-face')
                if special_effect:
                    special_effect_text = special_effect.text.strip()

            # Check if the special effect has already been printed
                    if not special_effect_printed:
                        #print(special_effect_text)
                        special_effect_printed = True
        with open("storage.py", "r", encoding="latin-1") as storage_file:
            for line in storage_file:
                data = ast.literal_eval(line)
                if data.get("character_name") == character_name:
                    # Character data found in storage, send the stored values
                    embed = discord.Embed(title=data["character_name"], description=data["description"] + "test", color=discord.Color.blue())
                    if formatted_materials_str != "None":
                        embed.add_field(name="**Materials:**", value=data["formatted_materials_str"], inline=True)

                    embed.add_field(name="**Information:**", value="`Tower Type:` " + data["damage_type1"] + "\n`Damage Type:` " + data["damage_type2"] + "\n`Secondary Damage Type:` " + data["damage_type3"] + "\n`Additional Information:` " + data["special_effect"], inline=True)
                    embed.add_field(name="**Normal Version:**", value="*"+data["caption1"]+"*", inline=False)
                    embed.set_image(url=data["non_shiny_image"])
                    embed.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")
                    embedVar = discord.Embed(description="**Shiny Version:**\n*"+data["caption2"]+"*",color=discord.Color.blue())
                    embedVar.set_image(url=data["shiny_image"])
                    embedVar.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")

                    await ctx.send(embed=embed)
                    await ctx.send(embed=embedVar)

                    return
        embed = discord.Embed(title=character_name,description=modified_text,color=discord.Color.blue())

        if formatted_materials_str != "None":
            embed.add_field(name="**Materials:**", value=formatted_materials_str, inline=True)
            
        embed.add_field(name="**Information:**", value="`Tower Type:` "+damage_type1 + "\n`Damage Type:` " + damage_type2 + "\n`Secondary Damage Type:` " + damage_type3 + "\n`Additional Information:` " + special_effect_text, inline=True)
        embed.add_field(name="**Normal Version:**", value="*"+caption1+"*", inline=False)
        embed.set_image(url=non_shiny_image)
        embed.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")
        embedVar = discord.Embed(description="**Shiny Version:**\n*"+caption2+"*",color=discord.Color.blue())
        embedVar.set_image(url=shiny_image)
        embedVar.set_footer(text="Anime Adventures Web Scraper powered by Jarvis.", icon_url="https://media.discordapp.net/attachments/1130781031511900252/1131308552330432632/aa.png")

        await ctx.send(embed=embed)
        await ctx.send(embed=embedVar)

        if ctx.author.id == 544776631672242176:  # Replace SPECIFIC_USER_ID with the actual ID of the specific user
            await ctx.send("Do you want to save the data? (y/n)")

            def check_response(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ['y', 'n']
            
            try:
                response = await client.wait_for('message', check=check_response, timeout=30)

                if response.content.lower() == 'y':
                # Save all the data into storage.py
                    data_to_save = {
                        "character_name": character_name,
                        "formatted_materials_str": formatted_materials_str,   
                        "description": modified_text,
                        "non_shiny_image": non_shiny_image,
                        "shiny_image": shiny_image,
                        "special_effect": special_effect_text,
                        "damage_type1": damage_type1,
                        "damage_type2": damage_type2,
                        "damage_type3": damage_type3,
                        "caption1": caption1,
                        "caption2": caption2
                    }

                # Save data to storage.py
                    with open("storage.py", "a") as storage_file:
                        storage_file.write(str(data_to_save) + "\n")

                    await ctx.send("Data saved successfully!")
                else:
                    await ctx.send("Data not saved.")

            except asyncio.TimeoutError:
                await ctx.send("You didn't respond in time. Data not saved.")

    except Exception as e:
        print(f"Error fetching information for {character_name}: {e}")
        traceback.print_exc()
        await print("Character not found or error occurred while fetching information.")

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
