import os
import csv
import subprocess

seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def main():
    pert_script_path = os.path.abspath("pert_scripts/perturb.py")
    deepgoplus_script_path = os.path.abspath("deepgoplus/main-no-diamond.py")
    pkl_script_path = os.path.abspath("convert_tsv_pkl.py")
    eval_script_path = os.path.abspath("evaluate_deepgoplus.py")
    pert_chance = 0.01
    filename = subprocess.run(
        ["python", pert_script_path, "-p", pert_chance, "-sp", "-s", "1"],
        stdout=subprocess.PIPE,
    )
    print("Perturbations added")

    filename_path = os.path.join(
        os.getcwd(), "perturb", filename.stdout.decode().strip()
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

    subprocess.run(["python", pkl_script_path])
    print("Converted to pickle")

    result_mf = subprocess.run(
        ["python", eval_script_path, "-o", "mf", "-tsdf", "results.pkl"],
        stdout=subprocess.PIPE,
    )
    format_result(result_mf, "results/deepgoplus_mf.csv", 1, pert_chance)

    print("Evaluated MF")

    result_bp = subprocess.run(
        ["python", eval_script_path, "-o", "bp", "-tsdf", "results.pkl"],
        stdout=subprocess.PIPE,
    )
    format_result(result_bp, "results/deepgoplus_bp.csv", 1, pert_chance)
    print("Evaluated BP")

    result_cc = subprocess.run(
        ["python", eval_script_path, "-o", "cc", "-tsdf", "results.pkl"],
        stdout=subprocess.PIPE,
    )
    format_result(result_cc, "results/deepgoplus_cc.csv", 1, pert_chance)
    print("Evaluated CC")


def format_result(results, filename, iteration, pert):
    metrics = results.stdout.decode("utf-8").split("\n")[-4:-1]
    with open(filename, "a+", newline="") as csv_writer:
        writer = csv.writer(csv_writer)
        # Write the header if the file is empty
        if csv_writer.tell() == 0:
            writer.write(["Iteration", "Smin", "Fmax", "AUPR", "Perturbation Chance"])
        line = ": ".join(metrics)
        values = line.split(": ")[1::2]
        writer.writerow([iteration, values[0], values[1], values[2], pert])


if __name__ == "__main__":
    main()
