import json
import numpy as np
from numpy import linalg as LA
import spacy
import operator
nlp = spacy.load('en_core_web_lg')

with open('avg_embed.json', 'r') as f:
    tree =  json.load(f)

with open('know-how.json', 'r') as f:
    ques = json.load(f)

with open('tags.txt', 'r') as f:
    data = f.readlines()

import pprint
pp = pprint.PrettyPrinter(indent=4)

def cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (LA.norm(vector1) * LA.norm(vector2))

personal_threshold = 0.8

def quora(tree, ques, doc, agg_score=0, relation=[]):
    score = {}
    if "children" in tree:
        for child in tree["children"]:
            personal = cosine_similarity(doc.vector, child["personal_embed"])
            loc_score = personal
            if "avg_embed" in child:
                avg = cosine_similarity(doc.vector, child["avg_embed"])
                loc_score += avg
                loc_score = loc_score/2
            score[child["name"]] = loc_score
        score = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
        # pp.pprint(score)
        if score[0][1] > agg_score:
            relation.append(score[0][0])
            agg_score += score[0][1]
            new_tree = (item for item in tree["children"] if item["name"] == score[0][0]).__next__()
            new_ques_tree = (item for item in ques["children"] if item["name"] == score[0][0]).__next__()
            quora(new_tree, new_ques_tree, doc, agg_score, relation)
        elif cosine_similarity(doc.vector, tree["personal_embed"]) > personal_threshold:
            if "personal_list" not in ques:
                ques["personal_list"] = []
            ques["personal_list"].append(data_instance)
            return
        else:
            if "reserve_list" not in ques:
                ques["reserve_list"] = []
            ques["reserve_list"].append(data_instance)
            return
    else:
        if cosine_similarity(doc.vector, tree["personal_embed"]) > personal_threshold:
            if "personal_list" not in ques:
                ques["personal_list"] = []
            ques["personal_list"].append(data_instance)
            return
        else:
            if "reserve_list" not in ques:
                ques["reserve_list"] = []
            ques["reserve_list"].append(data_instance)
            return
import re

for i in range(len(data)):
    # try:
    data_instance = data[i]
    question, tags = data[i].split('\t')
    tags = re.split('\| | \| |\n', tags)
    tag_list = list(filter(None, tags))
    score_list = []
    if len(tag_list) > 0:
        doc = nlp(' '.join(tag_list))
        relation = []
        quora(tree, ques, doc, 0, relation)
        related = ' --> '.join(relation)
        print(i, '\t', question, '\t', related)
        # exit()
        if not i % 100:
            with open('tree_without_brt.json', 'w') as outfile:
                import re
                output = json.dumps(ques, indent=4)
                outfile.write(re.sub(r'(?<=\d),\s+', ', ', output))