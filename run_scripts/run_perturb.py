import os
import csv
import subprocess
import click as ck

seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# pert_chances = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
pert_chances = [0.1]
cwd = os.getcwd()
pert_script_path = os.path.join(cwd, "pert_scripts", "perturb.py")
deepgoplus_script_path = os.path.join(cwd, "deepgoplus", "main-no-diamond.py")
pkl_script_path = os.path.abspath("convert_tsv_pkl.py")
eval_script_path = os.path.abspath("evaluate_deepgoplus.py")


def format_result(results: str, filename: str, iteration: int, pert: float):
    """Formats the result of the evaluate_deepgoplus script into a csv
        with Iteration, Smin, Fmax, AUPR as headers

    Args:
        results (str): Output of evaluate_deepgoplus script
        filename (str): Name of csv file to write to
        iteration (int): The index in which the evaluate_deepgoplus script was called in the loop
        pert (float): Perturbation chance ranging from 0 to 1
    """
    metrics = results.stdout.decode("utf-8").split("\n")[-4:-1]
    with open(os.path.join(cwd, "results", filename), "a+", newline="") as csv_writer:
        writer = csv.writer(csv_writer)
        # Write the header if the file is empty
        if csv_writer.tell() == 0:
            writer.writerow(
                ["Iteration", "Smin", "Fmax", "AUPR", "Perturbation Chance"]
            )
        line = ": ".join(metrics)
        values = line.split(": ")[1::2]
        writer.writerow([iteration, values[0], values[1], values[2], pert])


@ck.command()
@ck.option(
    "--type",
    "-t",
    default="insert",
    type=ck.Choice(["insert", "swap", "delete"]),
    help="Type of perturbation to apply",
)
def main(type):
    pert_chance = 0.1
    for pert_chance in pert_chances:
        for index, seed in enumerate(seeds):
            # Adds perturbations
            filename = ""
            if type == "delete":
                # TODO Change to delete script
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-sp",
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            elif type == "swap":
                # TODO Change to swap script when written
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-sp",
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            else:
                # Default is insert
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-sp",
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            print("Perturbations added")

            filename_path = os.path.join(
                cwd, "perturb", filename.stdout.decode().strip()
            )
            subprocess.run(
                [
                    "python",
                    deepgoplus_script_path,
                    "-dr",
                    "./data",
                    "-if",
                    filename_path,
                    "-t",
                    "0.3",
                ]
            )
            print("Deepgoplus evaluated")

            # Converts results.tsv from the deepgoplus script into a results.pkl
            subprocess.run(["python", pkl_script_path])
            print("Converted to pickle")

            # Creates a results folder if it doesn't exist
            if not os.path.exists("results"):
                os.makedirs("results")

            # Evaluate results
            ontologies = ["mf", "bp", "cc"]
            for ontology in ontologies:
                results = subprocess.run(
                    [
                        "python",
                        eval_script_path,
                        "-o",
                        ontology,
                        "-tsdf",
                        "results.pkl",
                    ],
                    stdout=subprocess.PIPE,
                )

                format_result(
                    results, f"deepgoplus_{ontology}_{type}.csv", index + 1, pert_chance
                )
                print(f"Evaluated {ontology.upper()}")


if __name__ == "__main__":
    main()
