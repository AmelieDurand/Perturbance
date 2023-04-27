import random
from typing import Callable
import click as ck
import os

# initialize LIST of useless characters + char <--- GLOBAL
dna_char = {"useless": list("BJOUXZ"), "main": list("ACDEFGHIKLMNPQRSTVWY")}


def insert(sample, p, char_type, spread):
    """Randomly select a spot to insert ONE thing by concatenating in 3 parts
    take in noise as list"""
    noise_ls = gen_noise(sample, p, char_type, spread)
    sample = list(sample)
    if not spread and len(noise_ls) > 1:
        noise_ls = unspread_noise(noise_ls, sample, p, char_type, spread)
    for noise in noise_ls:
        sample.insert(
            random.randint(1, len(sample)), noise
        )  # <-- MUST shuffle ls later
    return "".join(sample)


def gen_noise(sample, p, char_type, spread):  # <-- frequency probability
    """
    DECIDE what to insert to one of specific case (TOTAL 12 variations)
    --list of WHAT to insert: homogenous vs mixed
    --calculate HOW MANY to insert (frequency function of length): 0.1%, 1%, 10%
    --decide HOW to insert (together or spread)
    """
    length = len(sample)
    noise_ls = random.choices(char_type, k=round(p * length))
    random.shuffle(noise_ls)
    return noise_ls


def unspread_noise(noise: list, sample, p, char_type, spread):
    """
    Receive a list of noise where every element is 1 character,
    flip a coin while looping through the noise to decide
    whether to combine or not
    Note: it's possible to have 3 characters concatenated
    ! Only compatible with insert() for now
    """
    output = [noise[0]]
    for i in range(1, len(noise)):
        if random.randint(0, 1):  # flip coin to decide whether or not to combine
            output[-1] = output[-1] + noise[i]
        else:
            output.append(noise[i])
            output.append("")
    return [x for x in output if x]  # remove empty string


def substitute(sample, p, char_type, spread):
    """Randomly select a spot to insert ONE thing by concatenating in 3 parts
    take in noise as list"""
    noise_ls = gen_noise(sample, p, char_type, spread)
    sample = list(sample)
    for noise in noise_ls:
        i = random.randint(1, len(sample) - 1)
        sample[i] = noise
    return "".join(sample)


def swap(sample, p):
    """
    1 noise correspond to 1 swap
    will not swap last letter
    """
    length = len(sample)
    sample = list(sample)
    for rep in range(round(p * length)):
        i = random.randint(1, length - 1)
        sample[i - 1], sample[i] = sample[i], sample[i - 1]
    return "".join(sample)


def getPerturbation(type):
    """
    Switch statement that returns the perturbation function based on the
    given perturbation string.

    Args:
        type (str): type of perturbation to apple.

    Returns:
        Callable : The func that applies the requested perturbation
    """
    pert = {"insert": insert, "swap": swap, "substitution": substitute}
    return pert.get(type, "Invalid type. No perturbations found")


@ck.command()
@ck.option(
    "--perturbation",
    "-p",
    default=0.1,
    help="Perturbation chance to be applied ranging from 0 to 1",
)
@ck.option(
    "--type",
    "-t",
    default="insert",
    type=ck.Choice(["insert", "swap", "substitution"]),
    help="Type of perturbation to apply",
)
@ck.option(
    "--char-type",
    "-c",
    default="useless",
    help="Characters to use when perturbing data (useless or main)",
)
@ck.option("--spread", "-sp", is_flag=True, help="Perturbation in % to be applied")
@ck.option("--alpha", "-a", help="Id of the perturbation")
@ck.option("--seed", "-s", help="Seed for random")
def main(perturbation: float, type: str, char_type: str, spread: bool, alpha, seed):
    with open(os.path.join("/deepgoplus", "data", "test_data.fa"), "r") as f:
        database = f.readlines()
    if seed is not None:
        random.seed(seed)
    spread_text = "_spread" if spread else ""
    f_out = open(
        os.path.join(
            "/deepgoplus",
            "perturb",
            f"test_data_{type}_{str(perturbation)+dna_char[char_type][0]}_{str(alpha)}{spread_text}.fa",
        ),
        "w",
    )
    perturb: Callable = getPerturbation(type)
    for i in range(0, len(database), 2):
        f_out.write("\n" + database[i])
        if type == "swap":
            f_out.write(perturb(database[i + 1].strip(), perturbation))
        else:
            f_out.write(
                perturb(
                    database[i + 1].strip(), perturbation, dna_char[char_type], spread
                )
            )
    f_out.close()
    print(
        f"test_data_{type}_{str(perturbation)+dna_char[char_type][0]}_{str(alpha)}{spread_text}.fa"
    )


if __name__ == "__main__":
    main()
