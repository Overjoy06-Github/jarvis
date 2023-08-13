from bs4 import BeautifulSoup
import requests
from custom_emojis import custom_emojis

character = "Yoshina".title()
html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
soup = BeautifulSoup(html_text, 'html.parser')
character_names = requests.get('https://animeadventures.fandom.com/wiki/Unit_List').text
character_dict = BeautifulSoup(character_names, 'html.parser')

#character name | Metal Knight (Bofoi)
character_name = soup.find('h1', class_ = 'page-header__title')
character_name = ' '.join(character_name.stripped_strings)

#character evolution name | Metal Knight (Arsenal)
character_div = soup.find('div', class_ = 'mobile-hidden')
character_evolution_name = character_div.text.strip()

#description | Metal Knight  is a Mythical unit based on Metal Knight, from the anime One Punch Man. He is only obtainable through summons, and requires 5k kills to evolve.
description = soup.find('div', class_ = 'mw-parser-output').find('p')
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


# Captions for different versions | caption1 - normal | caption2 - shiny
captions = soup.find_all('figcaption', class_='pi-item-spacing pi-caption')
caption1 = captions[0].get_text(strip=True) if captions else "..."
if len(captions) > 1:
    caption2 = captions[1].get_text(strip=True)
else:
    caption2 = caption1

'''formatted_materials_str
# 1 Metal Knight
35 Full Power Core
12 Star Fruit
4 Star Fruit (Blue)
3 Star Fruit (Pink)
4 Star Fruit (Green)
1 Star Fruit (Rainbow)
'''
def format_material(material):
    quantity, item = material
    item = item.strip()

    # Handle different variations of "Star Fruit" separately
    if item.startswith("Star Fruit"):
        base_item = "StarFruit"
        if item in custom_emojis:
            emoji_id = custom_emojis[item]
            emoji_name = base_item + "".join([word.capitalize().replace('(', '_').replace(')', '').replace("'", "") for word in item.split()[2:]])
            return f"{quantity}x {item} <:{emoji_name}:{emoji_id}>"

    if item in custom_emojis:
        emoji_id = custom_emojis[item]
        emoji_name = item.replace(' ', '_').replace("'", "")  # Remove the apostrophe from the emoji name
        return f"{quantity}x {item} <:{emoji_name}:{emoji_id}>"
    else:
        return f"{quantity}x {item}"
    
# Your existing code
required_items_row = soup.select('table.article-table tr')[0]
td_elements = required_items_row.find_all('td')
materials = td_elements[1].get_text(strip=False).replace('Required Items:', '').replace('\n', '').split('x')
materials = [material.strip() for material in materials if material.strip()]

formatted_materials = [format_material(material.split(maxsplit=1)) for material in materials]
formatted_materials_str = '\n'.join(formatted_materials)

# Extract and download the images
image_elements = soup.find_all('img')
image_urls = [image['src'] for image in image_elements]

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
#damage_type3 = f"{damage_type3} {get_custom_emoji(damage_type3)}"

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
