import random


def delete(sample, p):
    sample = list(sample)
    length = len(sample)
    amount_deletions = int(length * p)
    indices_to_delete = random.sample(range(length), amount_deletions)
    for i in sorted(indices_to_delete, reverse=True):
        del sample[i]
    return "".join(sample)


# --------------------------------
# CHANGE THE OPTIONS HERE
p = 0.01

with open(".\\data\\test_data.fa", "r") as f:
    database = [line.strip() for line in f.readlines()]
f_out = open(f".\\test_data_delete_{str(p)}.fa", "w")
for i in range(0, len(database), 2):
    f_out.write(database[i] + "\n")
    f_out.write(delete(database[i + 1], p) + "\n")
f_out.close()
