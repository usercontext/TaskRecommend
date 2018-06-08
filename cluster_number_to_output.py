with open("cluster.txt") as f:
    data = f.readlines()

with open('test.csv') as f:
    ques = f.readlines()

data = data[1:]
op = {}
for i in data:
    line = i.split(' ')
    if line[1] not in op:
        op[line[1]] = []
    op[line[1]].append(ques[int(line[2])-1])

for key, value in op.items():
    val = list(set(value))
    op[key] = val

with open('output.csv', 'w') as f:
    for key, value in op.items():
        for i in value:
            f.write(i)
        f.write("\n")