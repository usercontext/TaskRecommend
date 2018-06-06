'''
This file used to use the old vector.json which is of a very bad format.
'''
from ontology import tree
import operator
import pandas as pd
import spacy
import json

nlp = spacy.load('en_core_web_lg')
df = pd.read_csv('quora.tsv', sep='\t')

df = df.loc[df['is_duplicate'] == 0]

tree_instant = {}
data1 = json.load(open('vector.json'))

tree_instant["root"] = data1

import numpy as np

from numpy import linalg as LA


def cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (LA.norm(vector1) * LA.norm(vector2))


for index, row in df.iterrows():
    file = open("relation_tree.txt", "a")
    question = row['question1']
    score = {}
    doc = nlp(question)
    relation = []
    for key, value in tree_instant["root"].items():
        maxi = cosine_similarity(doc.vector,
                                 tree_instant["root"][key]["KeyKeyKeyKey"])
        score[key] = maxi
    score = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
    # print(score)
    relation.append(score[0][0])
    inside_key = tree_instant["root"][score[0][0]]
    score1 = {}
    for key, value in inside_key.items():
        if key == "KeyKeyKeyKey":
            continue
        maxi = cosine_similarity(doc.vector, inside_key[key]["KeyKeyKeyKey"])
        score1[key] = maxi
    score1 = sorted(score1.items(), key=operator.itemgetter(1), reverse=True)
    # print(score1)
    relation.append(score1[0][0])
    in_inside_key = tree_instant["root"][score[0][0]][score1[0][0]]
    score2 = {}
    if in_inside_key:
        for key, value in in_inside_key.items():
            if key == "KeyKeyKeyKey":
                continue
            maxi = cosine_similarity(doc.vector, value)
            score2[key] = maxi
        score2 = sorted(
            score2.items(), key=operator.itemgetter(1), reverse=True)
        if len(score2) > 0:
            relation.append(score2[0][0])
    related = ' --> '.join(relation)
    print(index, '\t', question, '\t', related)
    file.write(str(index) + '\t' + question + '\t' + related + '\n')
    file.close()
