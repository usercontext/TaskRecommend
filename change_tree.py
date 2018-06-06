import json

tree_instant = {}

tree_instant["root"] = json.load(open('vector.json'))

data = {"name": "root", "children": []}

data1 = []
for key, value in tree_instant["root"].items():
    data2 = []
    for key1, value1 in value.items():
        if key1 != "KeyKeyKeyKey":
            data3 = []
            for key2, value2 in value1.items():
                if key2 != "KeyKeyKeyKey":
                    data3.append({"name": key2, "embedding": value2})
                else:
                    embedding1 = value2
            data2.append({"name": key1, "children": data3, "embedding": embedding1})
        else:
            embedding2 = value1
    data1.append({"name": key, "children": data2, "embedding": embedding2})
data["children"] = data1


with open('vector_new.json', 'w') as outfile:
    import re
    output = json.dumps(data, indent=4)
    outfile.write(re.sub(r'(?<=\d),\s+', ', ', output))