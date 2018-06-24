import json
import spacy
import numpy as np
nlp = spacy.load('en_core_web_lg')

with open('ques_list.json') as f:
    data = json.load(f)

def rec_embedding(data):
    embedding = np.zeros(300)
    print(data["name"])
    if "list" in data:
        for i in data["list"]:
            embedding += nlp(i.replace('-', ' ')).vector
        embedding = np.divide(embedding, len(data["list"]))

    data["personal_embed"] = embedding.tolist()

    if "children" in data:
        for i in data["children"]:
            rec_embedding(i)

rec_embedding(data)

with open('personal_embed.json', 'w') as f:
    import re
    output = json.dumps(data, indent=4)
    f.write(re.sub(r'(?<=\d),\s+', ', ', output))