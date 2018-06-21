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
    if not score_list:
        return True
    agg_score = float(sum(score_list)) + float(new_score)
    fractions = []
    for i in score_list:
        fractions.append(float(i) / float(agg_score))
    if max(fractions) < new_score / agg_score:
        return True
    else:
        return False

reserve_threshold = 10
from subprocess import Popen, PIPE
import csv

def new_node_check(tree, ques, reserve):
    #This is the threshold
    if len(reserve) > reserve_threshold:
        tag_mat = []
        for questags in reserve:
            question, tags = questags.split('\t')
            tags = re.split('\| | \| |\n', tags)
            tag_list = list(filter(None, tags))
            tag_mat.append(tag_list)

        similarity_mat = [[ nlp(' '.join(k)).similarity(nlp(' '.join(i))) for k in tag_mat] for i in tag_mat]
        distance_mat = [[ (1/k)-1 for k in i] for i in similarity_mat]
        with open("dist_mat.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(distance_mat)

        with open("corpus.csv", "w") as f:
            for item in tag_mat:
                f.write("%s\n" % " ".join(item))

        process = Popen(['Rscript', 'ddcrp/ddcrp.R'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(stdout, stderr)
        try:
            with open("cluster.txt", "r") as f:
                ddcrp_clust = f.readlines()

            ddcrp_clust = ddcrp_clust[1:]
            op = {}
            for i in ddcrp_clust:
                line = i.split(' ')
                if line[1] not in op:
                    op[line[1]] = []
                op[line[1]].append(reserve[int(line[2])-1])
            print("\n\n\n")
            for key, value in op.items():
                val = list(set(value))
                op[key] = val
            for key, value in op.items():
                for i in value:
                    print(i)

                print("\n")
        except Exception as e:
            print(e)
        new_node(tree, ques, op)
        reserve = []
        return True
    else:
        return False


def new_node(tree, ques, op):
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
        tree["children"].append({"name": "To be derived", "recommendations": value, "embedding": vector_sum.tolist()})
        ques["children"].append({"name": "To be derived", "recommendations": value })
    net_embedding = np.divide(net_embedding, len(op))
    #Accounting for leaves
    if len(tree["children"]) == len(op):
        tree["embedding"] = net_embedding.tolist()
    else:
        divfac = len(op) / len(tree["children"])
        new_embedding = np.asarray([(1-divfac)*i for i in tree["embedding"]]) + np.asarray([(divfac)*i for i in net_embedding.tolist()])
        tree["embedding"] = new_embedding.tolist()



def tree_construct(tree, ques, doc, prev_score=[], relation=[], score_list=[]):
    score = {}
    if "children" in tree:
        for lev in tree["children"]:
            maxi = cosine_similarity(doc.vector, lev["embedding"])
            score[lev["name"]] = maxi
        score = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
        try:
            if treesimscore(score[0][1], score_list):
                relation.append(score[0][0])
                score_list.append(score[0][1])
                new_tree = (item for item in tree["children"] if item["name"] == score[0][0]).__next__()
                new_ques_tree = (item for item in ques["children"] if item["name"] == score[0][0]).__next__()
                tree_construct(new_tree, new_ques_tree, doc, prev_score=score, relation=relation, score_list=score_list)
            else:
                if "recommendations" not in ques:
                    ques["recommendations"] = []
                ques["recommendations"].append(data_instance)
                new_node_check(tree, ques, ques["recommendations"])
                return
        except Exception as e:
            print(e)
            pass
    else:
        if "recommendations" not in ques:
            ques["recommendations"] = []
        ques["recommendations"].append(data_instance)
        new_node_check(tree, ques, ques["recommendations"])
        return


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
        # for lev1 in tree_instant["children"]:
        #     maxi = cosine_similarity(doc.vector, lev1["embedding"])
        #     score[lev1["name"]] = maxi
        # score = sorted(score.items(), key=operator.itemgetter(1), reverse=True)
        # # pp.pprint(score)
        # relation.append(score[0][0])
        # score_list.append(score[0][1])
        # inside_key = (item for item in tree_instant["children"] if item["name"] == score[0][0]).__next__()
        # ques_ins_key = (item for item in tree["children"] if item["name"] == score[0][0]).__next__()
        # score1 = {}
        # for lev2 in inside_key["children"]:
        #     maxi = cosine_similarity(doc.vector, lev2["embedding"])
        #     score1[lev2["name"]] = maxi
        # score1 = sorted(score1.items(), key=operator.itemgetter(1), reverse=True)
        # # pp.pprint(score1)
        # if treesimscore(score1[0][1], score_list):
        #     relation.append(score1[0][0])
        #     score_list.append(score1[0][1])
        #     in_inside_key = (item for item in inside_key["children"] if item["name"] == score1[0][0]).__next__()
        #     ques_in_ins_key = (item for item in ques_ins_key["children"] if item["name"] == score1[0][0]).__next__()
        #     score2 = {}
        #     if "children" in in_inside_key:
        #         for lev3 in in_inside_key["children"]:
        #             maxi = cosine_similarity(doc.vector, lev3["embedding"])
        #             score2[lev3["name"]] = maxi
        #         score2 = sorted(score2.items(), key=operator.itemgetter(1), reverse=True)
        #         if len(score2) > 0:
        #             if treesimscore(score2[0][1], score_list):
        #                 relation.append(score2[0][0])
        #                 ques_temp = (item for item in ques_in_ins_key["children"] if item["name"] == score2[0][0]).__next__()
        #                 if "recommendations" not in ques_temp:
        #                     ques_temp["recommendations"] = []
        #                 ques_temp["recommendations"].append(question)
        #             # pp.pprint(score2)
        #             else:
        #                 if "recommendations" not in ques_in_ins_key:
        #                     ques_in_ins_key["recommendations"] = []
        #                 ques_in_ins_key["recommendations"].append(question)
        # else:
        #     if "recommendations" not in ques_ins_key:
        #         ques_ins_key["recommendations"] = []
        #     ques_ins_key["recommendations"].append(question)
        tree_construct(tree_instant, tree, doc, relation=relation, score_list=score_list)
        related = ' --> '.join(relation)
        print(i, '\t', question, '\t', related)
        if not i % 100:
            with open('dynamic_tree.json', 'w') as outfile:
                import re
                output = json.dumps(tree, indent=4)
                outfile.write(re.sub(r'(?<=\d),\s+', ', ', output))

        # with open("relationtagstopping_recursive.txt", "a") as file:
        #     file.write(str(i) + '\t' + question + '\t' + related + '\n')

    # except Exception as e:
    #     print(e, "Failed")