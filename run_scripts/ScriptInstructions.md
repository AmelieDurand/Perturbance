# How to run DeepGoPlus & Perturbations 

# Deepgoplus
- Clone the github
- Have the data-1.0.6.tar.gz in your project
- Run Docker

  **FROM THE DOCKERFILE FOUND IN THE GITHUB**
  - docker build -t deepgoplus .
  - docker run --rm -it deepgoplus

**You're now in the deepgoplus container**

# Scripts

## Perturbation Scripts
All perturbation scripts have an optional ```-s``` CLI option for seeding
### Insert With Spread
```bash
python <path to insert_swap.py> -p <Perturbation Chance> -sp
```
### Insert without Spread
```bash
python <path to insert_swap.py> -p <Perturbation Chance>
```
### Swap
```bash
python <path to insert_swap.py> -t swap -p <Perturbation Chance>
```
### Delete
```bash
python <path to deletion.py> -p <Perturbation Chance>
```

## Run Scripts
**BEFORE RUNNING**
Add a folder called perturb
```bash
mkdir perturb
```

```bash
python <path to run_pert.py> -t <type>
```
Valid types include : "insert", "swap", "delete" & "insert-spread".

Each type refers to the perturbation script that will be run.

Defaults to insert-spread

The run script will 
- Add perturbations
- Run deepgoplus
- Run the convert_tsv_pkl.py script to turn the results.tsv into a results.pkl
- Evaluate the results in MF, BP & CC with the evaluate_deepgoplus.py script

The run script runs 10 alphas for each perturbation chance.
As of now the perturbation chances range from 0.1-0.9 in increments of 0.1
