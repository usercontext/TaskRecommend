import json

with open('know-how.json', 'r') as f:
    data = json.load(f)

#Get the questions
import requests
# from lxml import html
counter = 0
import re

regex = '(?<=href=\"\/\/www\.wikihow\.com\/)[A-Za-z\-]*(?=\")'
def scrape(data):
    category = data["name"]
    print(category)
    try:
        page = requests.get("https://www.wikihow.com/Category:" + category)
        pat = re.findall(regex, page.text)
        data["list"] = pat
    except Exception as e:
        print(e)
        print(category)

    if "children" in data:
        for child in data["children"]:
            scrape(child)


scrape(data)

with open('ques_list.json', 'w') as f:
    json.dump(data, f, indent=4, sort_keys=False)
# for j in tuplist:
#     page = requests.get("https://www.wikihow.com/Category:" + )
#     tree = html.fromstring(page.content)
#     href = tree.xpath('//div[contains(@class, "section minor_section")]/ul/li/a/@href')
#     title = tree.xpath('//div[contains(@class, "section minor_section")]/ul/li/a/text()')
#     print(title)
#     for i in range(len(href)):
#         counter = counter + 1
#         queslist.append((href[i], title[i]))

#     print(j[1], counter)

# with open("wikihow_question_nos.txt", "a") as f:
#     for i in range(len(queslist)):
#         f.write(str(i) + '\t' + queslist[i][1] + '\n')