import csv
import pandas as pd
import numpy as np
import pickle
import os

new_dict = {}
f = open(os.path.join("/deepgoplus", "data", "predictions.pkl"), "rb")
predictions = pickle.load(f)

f = open(
    os.path.join(
        "/deepgoplus",
        "results",
        f"results_{os.environ.get('SLURM_ARRAY_TASK_ID', '')}.tsv",
    )
)
f = csv.reader(f)
for line in f:
    line = line[0].split("\t")
    protein = line[0]
    new_dict[protein] = {}

    for i in line[1:]:
        i = i.split("|")
        new_dict[protein][i[0]] = np.float64(i[1])

df = pd.DataFrame(
    {
        "proteins": new_dict.keys(),
        "prop_annotations": [
            list(predictions.loc[predictions["proteins"] == x]["prop_annotations"])[0]
            for x in new_dict
        ],
        "preds": [list(new_dict[x].values()) for x in new_dict],
    }
)
df.to_pickle(
    os.path.join(
        "/deepgoplus",
        "results",
        f"results_{os.environ.get('SLURM_ARRAY_TASK_ID', '')}.pkl",
    )
)
