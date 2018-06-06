# '''
# This file decides on stopping the algorithm based on monotonicity.
# '''

import operator

import pandas as pd
import spacy
import json

# from pdb import set_trace as bp

#Loading NLP package
nlp = spacy.load('en_core_web_lg')

#Loading the data from Quora
df = pd.read_csv('quora.tsv', sep='\t')
df = df.loc[df['is_duplicate'] == 0]

#Loading Data from Quora Dataset
tree_instant = json.load(open('vector_new.json'))
tree = json.load(open('tree.json'))

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
    # try:
    question, tags = data[i].split('\t')
    tags = re.split('\| | \| |\n', tags)
    tag_list = list(filter(None, tags))
    score_list = []
    if len(tag_list) > 0:
        doc = nlp(' '.join(tag_list))
        score = {}
        relation = []
        for lev1 in tree_instant["children"]:
            maxi = cosine_similarity(doc.vector, lev1["embedding"])
            score[lev1["name"]] = maxi
        score = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
        # pp.pprint(score)
        relation.append(score[0][0])
        score_list.append(score[0][1])
        inside_key = (item for item in tree_instant["children"] if item["name"] == score[0][0]).__next__()
        ques_ins_key = (item for item in tree["children"] if item["name"] == score[0][0]).__next__()
        score1 = {}
        for lev2 in inside_key["children"]:
            maxi = cosine_similarity(doc.vector, lev2["embedding"])
            score1[lev2["name"]] = maxi
        score1 = sorted(score1.items(), key=operator.itemgetter(1), reverse=True)
        # pp.pprint(score1)
        if treesimscore(score1[0][1], score_list):
            relation.append(score1[0][0])
            score_list.append(score1[0][1])
            in_inside_key = (item for item in inside_key["children"] if item["name"] == score1[0][0]).__next__()
            ques_in_ins_key = (item for item in ques_ins_key["children"] if item["name"] == score1[0][0]).__next__()
            score2 = {}
            if "children" in in_inside_key:
                for lev3 in in_inside_key["children"]:
                    maxi = cosine_similarity(doc.vector, lev3["embedding"])
                    score2[lev3["name"]] = maxi
                score2 = sorted(score2.items(), key=operator.itemgetter(1), reverse=True)
                if len(score2) > 0:
                    if treesimscore(score2[0][1], score_list):
                        relation.append(score2[0][0])
                        ques_temp = (item for item in ques_in_ins_key["children"] if item["name"] == score2[0][0]).__next__()
                        if "recommendations" not in ques_temp:
                            ques_temp["recommendations"] = []
                        ques_temp["recommendations"].append(question)
                    # pp.pprint(score2)
                    else:
                        if "recommendations" not in ques_in_ins_key:
                            ques_in_ins_key["recommendations"] = []
                        ques_in_ins_key["recommendations"].append(question)
        else:
            if "recommendations" not in ques_ins_key:
                ques_ins_key["recommendations"] = []
            ques_ins_key["recommendations"].append(question)
        related = ' --> '.join(relation)
        print(i, '\t', question, '\t', related)
        if not i % 1:
            with open("dictques_stop.json", "w") as buck:
                json.dump(tree, buck, indent=4, sort_keys=True)

        with open("relationtagstopping.txt", "a") as file:
            file.write(str(i) + '\t' + question + '\t' + related + '\n')

    # except Exception as e:
    #     print(e, "Failed")