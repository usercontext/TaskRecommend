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

def likelihood(exude, collapse, temp3):
    return random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)

def new_node_child(tree, ques, op):
    if "children" not in tree:
        tree["children"] = []
        ques["children"] = []
    no_of_children = len(tree["children"])
    net_embedding = np.zeros(300)
    for key, value in op.items():
        vector_sum = np.zeros(300)
        for k in value:
            question, tags = k.split('\t')
            tags = re.split('\| | \| |\n', tags)
            tag_list = list(filter(None, tags))
            if len(tag_list) > 0:
                doc = nlp(' '.join(tag_list))
                vector_sum += doc.vector
        vector_sum = np.divide(vector_sum, len(value))
        net_embedding += vector_sum
        tree["children"].append({"name": "anonymoustag", "reserve": value, "embedding": vector_sum.tolist()})
        ques["children"].append({"name": "anonymoustag", "reserve": value })
    net_embedding = np.divide(net_embedding, len(op))
    #Accounting for leaves
    if len(tree["children"]) == len(op):
        tree["embedding"] = net_embedding.tolist()
    else:
        divfac = len(op) / len(tree["children"])
        new_embedding = np.asarray([(1-divfac)*i for i in tree["embedding"]]) + np.asarray([(divfac)*i for i in net_embedding.tolist()])
        tree["embedding"] = new_embedding.tolist()

def quora(tree, ques, doc, prev_score=0, relation=[]):
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
        if score[0][1] > prev_score*0.95:
            relation.append(score[0][0])
            prev_score = score[0][1]
            new_tree = (item for item in tree["children"] if item["name"] == score[0][0]).__next__()
            new_ques_tree = (item for item in ques["children"] if item["name"] == score[0][0]).__next__()
            quora(new_tree, new_ques_tree, doc, prev_score, relation)
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
            with open('tree_without_brt1.json', 'w') as outfile:
                import re
                output = json.dumps(ques, indent=4)
                outfile.write(re.sub(r'(?<=\d),\s+', ', ', output))