from bs4 import BeautifulSoup
import requests
import re

character = "Metal_Knight"
html_text = requests.get(f'https://animeadventures.fandom.com/wiki/{character}').text
soup = BeautifulSoup(html_text, 'lxml')
character_needed = soup.find('strong', class_ = 'mw-selflink selflink').text #prints the character
character_evolution_name = soup.find('div', class_ = 'mobile-hidden').text # prints Guts (Berserk)
description = soup.find('div', class_ = 'mw-parser-output').find('p').text
description = description.replace("MythicalMythical", "Mythical")
banner_raw = soup.find('figure', class_ = 'pi-item pi-image').find('img').get('src') # prints image link
imgs = soup.findAll('div', class_ = 'mw-parser-output')

images = []
for div in imgs:
    img_tags = div.findAll('img')
    for img in img_tags:
        src = img['src']
        if 'static' in src:
            images.append(src)
# 0 - egg of king
# 1 - non-shiny of unit
# 2 - shiny of unit
# 3 - 1st element of unit (physical/magic/true)
# 4 - 2nd element of unit (fire, wind, etc.)

evolution_materials = soup.find('table', class_='article-table game-font-face').text
split_text = re.split(r"(x\d+)\s*", evolution_materials)
transformed_text = ' '.join(split_text)
final = transformed_text.split()
final = final[:-5]

def listToString(s):
    str1 = " ".join(s)
    return str1

actual_final = listToString(final)

actual_final = listToString(final)
actual_final = re.sub(r"\bStar Fruit \(Blue\)(?!\S)", r"Star Fruit <:Star_Fruit_Blue:1131211288454905956>", actual_final)
actual_final = re.sub(r"\bStar Fruit \(Green\)(?!\S)", r"Star Fruit (Green) <:Star_Fruit_Green:1131211294058496081>", actual_final)
actual_final = re.sub(r"\bStar Fruit \(Pink\)(?!\S)", r"Star Fruit (Pink) <:Star_Fruit_Pink:1131211253486989413>", actual_final)
actual_final = re.sub(r"\bStar Fruit \(Rainbow\)(?!\S)", r"Star Fruit (Rainbow) <:Star_Fruit_Rainbow:1131211258696319016>", actual_final)
actual_final = re.sub(r"\bStar Fruit \(Red\)(?!\S)", r"Star Fruit (Red) <:Star_Fruit_Red:1131211261602955294>", actual_final)

actual_final = actual_final.replace("x", "\nx")
print(actual_final)
print(character_evolution_name)
