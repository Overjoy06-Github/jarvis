from bs4 import BeautifulSoup
import requests
import re

character = "Heathcliff".title()
html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
soup = BeautifulSoup(html_text, 'html.parser')

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
caption1 = captions[0].get_text(strip=True)
caption2 = captions[1].get_text(strip=True)

print(caption1)
print(caption2)
'''formatted_materials_str
# 1 Metal Knight
35 Full Power Core
12 Star Fruit
4 Star Fruit (Blue)
3 Star Fruit (Pink)
4 Star Fruit (Green)
1 Star Fruit (Rainbow)
'''
required_items_row = soup.select('table.article-table tr')[0]
td_elements = required_items_row.find_all('td')
materials = td_elements[1].get_text(strip=False).replace('Required Items:', '').replace('\n', '').split('x')
materials = [material.strip() for material in materials if material.strip()]
def format_material(material):
    return f"{material[0]}x {material[1]}"

formatted_materials = [format_material(material.split(maxsplit=1)) for material in materials]
formatted_materials_str = '\n'.join(formatted_materials)



# Extract and download the images
image_elements = soup.find_all('img')
image_urls = [image['src'] for image in image_elements]
