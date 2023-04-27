import os
import random
import click as ck


def delete(sample, p):
    sample = list(sample)
    length = len(sample)
    amount_deletions = int(length * p)
    indices_to_delete = random.sample(range(length), amount_deletions)
    for i in sorted(indices_to_delete, reverse=True):
        del sample[i]
    return "".join(sample)


@ck.command()
@ck.option(
    "--perturbation",
    "-p",
    default=0.01,
    help="Perturbation chance to be applied ranging from 0 to 1",
)
@ck.option("--alpha", "-a", help="Id of the perturbation")
@ck.option("--seed", "-s", help="Seed for random")
def main(perturbation, alpha, seed):
    with open(os.path.join("/deepgoplus", "data", "test_data.fa"), "r") as f:
        database = [line.strip() for line in f.readlines()]
    if seed is not None:
        random.seed(seed)
    f_out = open(
        os.path.join(
            "/deepgoplus",
            "perturb",
            f"test_data_delete_{str(perturbation)}_{str(alpha)}.fa",
        ),
        "w",
    )
    for i in range(0, len(database), 2):
        f_out.write(database[i] + "\n")
        f_out.write(delete(database[i + 1], perturbation) + "\n")
    f_out.close()
    print(
        os.path.join(
            "/deepgoplus",
            "perturb",
            f"test_data_delete_{str(perturbation)}_{str(alpha)}.fa",
        )
    )


if __name__ == "__main__":
    main()
