with open("test.csv") as f:
    data = f.readlines()

dist_mat = []
import spacy
import numpy
import math
import csv
nlp = spacy.load('en_core_web_lg')

for i in data:
    loc_mat = []
    for j in data:
        loc_mat.append(nlp(i).similarity(nlp(j)))
    dist_mat.append(loc_mat)

distance_mat = [[ (1/k)-1 for k in i] for i in dist_mat]

with open("foo.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(distance_mat)