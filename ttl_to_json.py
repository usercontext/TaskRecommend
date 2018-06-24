# Create tuples
import csv
with open("wikiHow_categories_hierarchy.ttl") as f:
    reader = csv.reader(f)
    data = list(list(rec) for rec in csv.reader(f, delimiter='\t'))

# print(data[0])
import re
articles = ['a', 'an', 'of', 'the', 'is', 'and', 'for']

def title_except(s, exceptions):
    word_list = re.split('-', s)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in exceptions else word.capitalize())
    return "-".join(final)

def cleanup(val):
    new_val = ""
    if val.startswith('ns1'):
        new_val = val[4:]
    elif val.startswith(''):
        new_val = val.replace("<http://www.wikihow.com/category:", "")
        new_val = new_val[:-1]

    return title_except(new_val, articles)


# print(cleanup('finance-and-business'))

new_data = [(cleanup(val[0]), cleanup(val[2][:-2])) for val in data]

print(new_data[1])


# a = [(1, 1), (4, 3), (5, 3), (6, 3), (7, 7), (8, 7), (9, 7), (2, 1), (3, 1)]

a = new_data
# print(a)
# pass 1: create nodes dictionary
nodes = {}
for i in a:
    id, parent_id = i
    nodes[id] = {'name': id}

# pass 2: create trees and parent-child relations
forest = []
for i in a:
    id, parent_id = i
    node = nodes[id]

    # either make the node a new tree or link it to its parent
    if id == parent_id:
        # start a new tree in the forest
        forest.append(node)
    else:
        # add new_node as child to parent
        parent = nodes[parent_id]
        if not 'children' in parent:
            # ensure parent has a 'children' field
            parent['children'] = []
        children = parent['children']
        children.append(node)

import json

with open('know-how.json', 'w') as f:
    json.dump(forest[0], f, indent=4)