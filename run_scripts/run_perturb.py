import os
import csv
import subprocess
import click as ck

seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
pert_chances = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
pert_script_path = os.path.join("/deepgoplus", "pert_scripts", "insert_swap.py")
del_script_path = os.path.join("/deepgoplus", "pert_scripts", "deletion.py")
deepgoplus_script_path = os.path.join("/deepgoplus", "deepgoplus", "main-no-diamond.py")
pkl_script_path = os.path.join("/deepgoplus", "convert_tsv_pkl.py")
eval_script_path = os.path.join("/deepgoplus", "evaluate_deepgoplus.py")


def format_result(results: str, filename: str, iteration: int, pert: float):
    """
    Formats the result of the evaluate_deepgoplus script into a csv
        with Iteration, Smin, Fmax, AUPR as headers

    Args:
        results (str): Output of evaluate_deepgoplus script
        filename (str): Name of csv file to write to
        iteration (int): The index in which the evaluate_deepgoplus script was called in the loop
        pert (float): Perturbation chance ranging from 0 to 1
    """
    metrics = results.stdout.decode("utf-8").split("\n")[-4:-1]
    with open(
        os.path.join("/deepgoplus", "metrics", filename), "a+", newline=""
    ) as csv_writer:
        writer = csv.writer(csv_writer)
        # Write the header if the file is empty
        if csv_writer.tell() == 0:
            writer.writerow(
                ["Iteration", "Smin", "Fmax", "AUPR", "Perturbation Chance"]
            )
        line = ": ".join(metrics)
        values = line.split(": ")[1::2]
        writer.writerow([iteration, values[0], values[1], values[2], pert])


class CLICommand(ck.Command):
    """
    A custom Command class that handles option dependency

    This custome class will throw an error if the letters option is used with anythign but insert or insert-spread.
    It will also throw an error if it's not used when type is insert or insert-spread
    """

    def invoke(self, ctx):
        if ctx.params.get("type") in [
            "insert",
            "insert-spread",
            "substitution",
            "substitution-spread",
        ] and ctx.params.get("char_type") not in ["useless", "main"]:
            # Default value for char_type is useless
            ctx.params.update({"char_type": "useless"})
        if ctx.params.get("type") not in [
            "insert",
            "insert-spread",
            "substitution",
            "substitution-spread",
        ] and ctx.params.get("char_type") in ["useless", "main"]:
            raise ck.BadOptionUsage(
                "char_type",
                "Cannot specify char-type when type is not insert, insert-spread, substitution or substitution-spread",
            )
        return super().invoke(ctx)


@ck.command(cls=CLICommand)
@ck.option(
    "--type",
    "-t",
    default="insert-spread",
    type=ck.Choice(
        [
            "swap",
            "delete",
            "insert",
            "insert-spread",
            "substitution",
            "substitution-spread",
        ]
    ),
    help="Type of perturbation to apply",
)
@ck.option(
    "--char-type",
    "-c",
    required=False,
    type=ck.Choice(["useless", "main"]),
    help="Type of letters to used when inserting. Can only be used when type is insert or insert-spread. Defaults to useless",
)
def main(type: str, char_type: str):
    """
    Perturbs data and measures the metrics of the DeepGoPlus model.

    Runs the proper perturbation on the test file, runs the DeepGoPlus model on that newly perturbed file,
    Turns results into a pickle file, measures the metrics for BP, CC and MF ontologies and writes them into csv files.
    Runs for 10 alphas for each pertubation. Pertubation range from 0.1 to 0.9 in increments of 0.1

    Args:
        type (str): Type of perturbation to apply
        char_type (str): Only when perturbation is insert or insert-spread. Types of characters to insert
    """
    for pert_chance in pert_chances:
        for index, seed in enumerate(seeds):
            # Adds perturbations
            filename = ""
            if type == "delete":
                filename = subprocess.run(
                    [
                        "python",
                        del_script_path,
                        "-p",
                        str(pert_chance),
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            elif type == "swap":
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-t",
                        type,
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            elif type == "substitution":
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-t",
                        type,
                        "-c",
                        char_type,
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            elif type == "substitution-spread":
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-t",
                        "substitution",
                        "-sp",
                        "-c",
                        char_type,
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            elif type == "insert":
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-t",
                        type,
                        "-c",
                        char_type,
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            else:
                # Default is insert-spread
                filename = subprocess.run(
                    [
                        "python",
                        pert_script_path,
                        "-p",
                        str(pert_chance),
                        "-t",
                        "insert",
                        "-c",
                        char_type,
                        "-sp",
                        "-a",
                        str(index),
                        "-s",
                        str(seed),
                    ],
                    stdout=subprocess.PIPE,
                )
            print("Perturbations added")
            # Get path to the perturb data
            filename_path = os.path.join(
                "/deepgoplus", "perturb", filename.stdout.decode().strip()
            )
            # Run DeepGoPlus
            out = subprocess.run(
                [
                    "python",
                    deepgoplus_script_path,
                    "-dr",
                    os.path.join("/deepgoplus", "data"),
                    "-if",
                    filename_path,
                    "-t",
                    "0.3",
                ]
            )
            print("DeepGoPlus evaluated")

            # Converts results.tsv from the deepgoplus script into a results.pkl
            subprocess.run(["python", pkl_script_path])
            print("Converted to pickle")

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
                        os.path.join(
                            "/deepgoplus",
                            "results",
                            f"results_{os.environ.get('SLURM_ARRAY_TASK_ID', '')}.pkl",
                        ),
                    ],
                    stdout=subprocess.PIPE,
                )
                if type in [
                    "insert",
                    "insert-spread",
                    "substitution",
                ]:
                    format_result(
                        results,
                        f"deepgoplus_{ontology}_{type}_{char_type}.csv",
                        index + 1,
                        pert_chance,
                    )
                else:
                    format_result(
                        results,
                        f"deepgoplus_{ontology}_{type}.csv",
                        index + 1,
                        pert_chance,
                    )
                print(f"Evaluated {ontology.upper()}")


if __name__ == "__main__":
    main()
