'''
This file used the new json file created in the right format which is name, children, embedding.
'''
import operator

import pandas as pd
import spacy
import json

from pdb import set_trace as bp

nlp = spacy.load('en_core_web_lg')
df = pd.read_csv('quora.tsv', sep='\t')

df = df.loc[df['is_duplicate'] == 0]

tree_instant = {}

tree_instant["root"] = json.load(open('vector.json'))

import numpy as np

from numpy import linalg as LA


def cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (LA.norm(vector1) * LA.norm(vector2))


import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
with open('tags.txt') as f:
    data = f.readlines()

def treesimscore(new_score, score_list):
    agg_score = float(sum(score_list)) + float(new_score)
    fractions = []
    for i in score_list:
        fractions.append(float(i) / float(agg_score))
    if max(fractions) < new_score / agg_score:
        return True
    else:
        return False


for i in range(len(data)):
    try:
        question, tags = data[i].split('\t')
        tags = re.split('\| | \| |\n', tags)
        tag_list = list(filter(None, tags))
        score_list = []
        if len(tag_list) > 0:
            doc = nlp(' '.join(tag_list))
            score = {}
            relation = []
            for key, value in tree_instant["root"].items():
                maxi = cosine_similarity(
                    doc.vector, tree_instant["root"][key]["KeyKeyKeyKey"])
                score[key] = maxi
            score = sorted(
                score.items(), key=operator.itemgetter(1), reverse=True)
            # pp.pprint(score)
            relation.append(score[0][0])
            score_list.append(score[0][1])
            inside_key = tree_instant["root"][score[0][0]]
            ques_ins_key = data_instant["root"][score[0][0]]
            score1 = {}
            for key, value in inside_key.items():
                if key == "KeyKeyKeyKey":
                    continue
                maxi = cosine_similarity(doc.vector,
                                         inside_key[key]["KeyKeyKeyKey"])
                score1[key] = maxi
            score1 = sorted(
                score1.items(), key=operator.itemgetter(1), reverse=True)
            # pp.pprint(score1)
            if treesimscore(score1[0][1], score_list):
                relation.append(score1[0][0])
                score_list.append(score1[0][1])
                in_inside_key = tree_instant["root"][score[0][0]][score1[0][0]]
                ques_in_ins_key = data_instant["root"][score[0][0]][score1[0][
                    0]]
                score2 = {}
                if in_inside_key:
                    for key, value in in_inside_key.items():
                        if key == "KeyKeyKeyKey":
                            continue
                        maxi = cosine_similarity(doc.vector, value)
                        score2[key] = maxi
                    score2 = sorted(
                        score2.items(),
                        key=operator.itemgetter(1),
                        reverse=True)
                    if len(score2) > 0:
                        if treesimscore(score2[0][1], score_list):
                            relation.append(score2[0][0])
                            ques_in_ins_key[score2[0][0]].append(question)
                        # pp.pprint(score2)
                else:
                    try:
                        ques_ins_key["HereHereHereHere"].append(question)
                    except:
                        ques_ins_key["HereHereHereHere"] = []
                        ques_ins_key["HereHereHereHere"].append(question)
            else:
                try:
                    ques_ins_key["HereHereHereHere"].append(question)
                except:
                    ques_ins_key["HereHereHereHere"] = []
                    ques_ins_key["HereHereHereHere"].append(question)
            related = ' --> '.join(relation)
            print(i, '\t', question, '\t', related)
            if not i % 1:
                with open("dictques_stop.json", "w") as buck:
                    json.dump(data_instant, buck, indent=4, sort_keys=True)

            with open("relationtagstopping.txt", "a") as file:
                file.write(str(i) + '\t' + question + '\t' + related + '\n')

    except Exception as e:
        print(e, "Failed")