#!/usr/bin/env python

import numpy as np
import pandas as pd
import click as ck
from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import cosine_similarity
import sys
from collections import deque
import time
import logging
from sklearn.metrics import roc_curve, auc, matthews_corrcoef
from scipy.spatial import distance
from scipy import sparse
import math
from utils import FUNC_DICT, Ontology, NAMESPACES
from matplotlib import pyplot as plt
import json
import os
import pickle

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


@ck.command()
@ck.option("--data-root", "-dr", default="deepgoplus/data", help="Data root folder")
@ck.option(
    "--train-data-file",
    "-trdf",
    default="/deepgoplus/data/train_data.pkl",
    help="Data file with training features",
)
@ck.option(
    "--test-data-file",
    "-tsdf",
    default="/deepgoplus/data/predictions.pkl",
    help="Test data file",
)
@ck.option(
    "--terms-file",
    "-tf",
    default="/deepgoplus/data/terms.pkl",
    help="Data file with sequences and complete set of annotations",
)
@ck.option(
    "--diamond-scores-file",
    "-dsf",
    default="/deepgoplus/data/test_diamond.res",
    help="Diamond output",
)
@ck.option("--ont", "-o", default="mf", help="GO subontology (bp, mf, cc)")
@ck.option("--alpha", "-a", default=50, help="Alpha for for combining scores")
@ck.option("--score-file", "-sf", default="/workdir/eval_score_file")
def main(
    data_root,
    train_data_file,
    test_data_file,
    terms_file,
    diamond_scores_file,
    ont,
    alpha,
    score_file,
):
    if os.path.exists(data_root):
        train_data_file = os.path.join(data_root, train_data_file)
        # test_data_file = os.path.join(data_root, test_data_file)
        terms_file = os.path.join(data_root, terms_file)
        diamond_scores_file = os.path.join(data_root, diamond_scores_file)
        last_release_metadata = os.path.join(data_root, "metadata/last_release.json")
        go_rels = Ontology(os.path.join(data_root, "data/go.obo"), with_rels=True)

    # last_release_metadata = 'data-1.0.6/metadata/last_release.json'
    last_release_metadata = "/deepgoplus/metadata/last_release.json"
    with open(last_release_metadata, "r") as f:
        last_release_data = json.load(f)
        alpha = last_release_data["alphas"][ont]

    go_rels = Ontology("/deepgoplus/data/go.obo", with_rels=True)
    terms_df = pd.read_pickle(terms_file)
    terms = terms_df["terms"].values.flatten()
    terms_dict = {v: i for i, v in enumerate(terms)}

    train_df = pd.read_pickle(train_data_file)
    test_df = pd.read_pickle(test_data_file)
    print("Length of test set: " + str(len(test_df)))

    annotations = train_df["prop_annotations"].values
    annotations = list(map(lambda x: set(x), annotations))
    # annotations = [sorted(list(i)) for i in annotations]
    # print(annotations)
    test_annotations = test_df["prop_annotations"].values
    test_annotations = list(map(lambda x: set(x), test_annotations))
    # test_annotations = [sorted(list(i)) for i in test_annotations]
    go_rels.calculate_ic(
        [sorted(list(i)) for i in annotations]
        + [sorted(list(i)) for i in test_annotations]
    )

    # Print IC values of terms
    ics = {}
    for term in terms:
        ics[term] = go_rels.get_ic(term)

    prot_index = {}
    for i, row in enumerate(train_df.itertuples()):
        prot_index[row.proteins] = i

    # BLAST Similarity (Diamond)
    diamond_scores = {}
    with open(diamond_scores_file) as f:
        for line in f:
            it = line.strip().split()
            if it[0] not in diamond_scores:
                diamond_scores[it[0]] = {}
            diamond_scores[it[0]][it[1]] = float(it[2])

    blast_preds = []
    # print('Diamond preds')
    for i, row in enumerate(test_df.itertuples()):
        annots = {}
        prot_id = row.proteins
        # BlastKNN
        if prot_id in diamond_scores:
            sim_prots = diamond_scores[prot_id]
            allgos = set()
            total_score = 0.0
            for p_id, score in sim_prots.items():
                allgos |= annotations[prot_index[p_id]]
                total_score += score
            allgos = list(sorted(allgos))  # modification
            sim = np.zeros(len(allgos), dtype=np.float32)
            for j, go_id in enumerate(allgos):
                s = 0.0
                for p_id, score in sim_prots.items():
                    if go_id in annotations[prot_index[p_id]]:
                        s += score
                sim[j] = s / total_score
            ind = np.argsort(-sim)
            for go_id, score in zip(allgos, sim):
                annots[go_id] = score
        blast_preds.append(annots)

    # DeepGOPlus
    go_set = go_rels.get_namespace_terms(NAMESPACES[ont])
    go_set.remove(FUNC_DICT[ont])
    labels = test_df["prop_annotations"].values
    labels = list(map(lambda x: set(filter(lambda y: y in go_set, x)), labels))
    labels = [sorted(list(i)) for i in labels]  # modification
    # print(len(go_set))
    deep_preds = []
    # alphas = {NAMESPACES['mf']: 0.55, NAMESPACES['bp']: 0.59, NAMESPACES['cc']: 0.46}
    alphas = {NAMESPACES["mf"]: 0, NAMESPACES["bp"]: 0, NAMESPACES["cc"]: 0}

    with open(last_release_metadata, "r") as f:
        last_release_data = json.load(f)
        alpha = last_release_data["alphas"][ont]
        alphas[NAMESPACES[ont]] = alpha

    for i, row in enumerate(test_df.itertuples()):
        annots_dict = blast_preds[i].copy()
        for go_id in annots_dict:
            annots_dict[go_id] *= alphas[go_rels.get_namespace(go_id)]

        for j, score in enumerate(row.preds):
            go_id = terms[j]
            score *= 1 - alphas[go_rels.get_namespace(go_id)]

            if go_id in annots_dict:
                annots_dict[go_id] += score
            else:
                annots_dict[go_id] = score
        deep_preds.append(annots_dict)
    # print('AUTHOR DeepGOPlus')
    # print('MODEL 1')
    # print('KEYWORDS sequence alignment.')
    # for i, row in enumerate(test_df.itertuples()):
    #     prot_id = row.proteins
    #     for go_id, score in deep_preds[i].items():
    #         print(f'{prot_id}\t{go_id}\t{score:.2f}')
    # print('END')
    # return

    # Propagate scores
    # deepgo_preds = []
    # for annots_dict in deep_preds:
    #     annots = {}
    #     for go_id, score in annots_dict.items():
    #         for a_id in go_rels.get_anchestors(go_id):
    #             if a_id in annots:
    #                 annots[a_id] = max(annots[a_id], score)
    #             else:
    #                 annots[a_id] = score
    #     deepgo_preds.append(annots)

    # print('Computing Fmax')
    fmax = 0.0
    tmax = 0.0
    precisions = []
    recalls = []
    smin = 1000000.0
    rus = []
    mis = []
    for t in range(1, 101):  # the range in this loop has influence in the AUPR output
        threshold = t / 100.0
        preds = []
        for i, row in enumerate(test_df.itertuples()):
            annots = set()
            for go_id, score in deep_preds[i].items():
                if score >= threshold:
                    annots.add(go_id)

            new_annots = set()
            for go_id in annots:
                new_annots |= go_rels.get_anchestors(go_id)
            new_annots = sorted(list(new_annots))  # modification
            preds.append(new_annots)

        # Filter classes
        preds = list(map(lambda x: set(filter(lambda y: y in go_set, x)), preds))
        preds = [sorted(list(i)) for i in preds]  # modification
        fscore, prec, rec, s, ru, mi, fps, fns = evaluate_annotations(
            go_rels, labels, preds
        )
        avg_fp = sum(map(lambda x: len(x), fps)) / len(fps)
        avg_ic = sum(
            map(lambda x: sum(map(lambda go_id: go_rels.get_ic(go_id), x)), fps)
        ) / len(fps)
        # print(f'{avg_fp} {avg_ic}')
        precisions.append(prec)
        recalls.append(rec)
        # print(f'Fscore: {fscore}, Precision: {prec}, Recall: {rec}, S: {s}, RU: {ru}, MI: {mi}, threshold: {threshold}')
        if fmax < fscore:
            fmax = fscore
            tmax = threshold
        if smin > s:
            smin = s

    print(f"threshold: {tmax}")
    print(f"Smin: {smin}")
    print(f"Fmax: {fmax}")
    precisions = np.array(precisions)
    recalls = np.array(recalls)
    sorted_index = np.argsort(recalls)
    recalls = recalls[sorted_index]
    precisions = precisions[sorted_index]
    aupr = np.trapz(precisions, recalls)
    print(f"AUPR: {aupr}")
    # plt.figure()
    # lw = 2
    # plt.plot(
    #     recalls,
    #     precisions,
    #     color="darkorange",
    #     lw=lw,
    #     label=f"AUPR curve (area = {aupr:0.2f})",
    # )
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel("Recall")
    # plt.ylabel("Precision")
    # plt.title("Area Under the Precision-Recall curve")
    # plt.legend(loc="lower right")
    # plt.savefig(f'results/aupr_{ont}_{alpha:0.2f}.pdf')
    # df = pd.DataFrame({'precisions': precisions, 'recalls': recalls})
    # df.to_pickle(f'results/PR_{ont}_{alpha:0.2f}.pkl')


def compute_roc(labels, preds):
    # Compute ROC curve and ROC area for each class
    fpr, tpr, _ = roc_curve(labels.flatten(), preds.flatten())
    roc_auc = auc(fpr, tpr)
    return roc_auc


def compute_mcc(labels, preds):
    # Compute ROC curve and ROC area for each class
    mcc = matthews_corrcoef(labels.flatten(), preds.flatten())
    return mcc


def evaluate_annotations(go, real_annots, pred_annots):
    total = np.float64(0.0)
    p = 0.0
    r = 0.0
    p_total = 0.0
    ru = np.float64(0.0)
    mi = np.float64(0.0)
    fps = []
    fns = []
    for i in range(len(real_annots)):
        if len(real_annots[i]) == 0:
            continue
        tp = set(real_annots[i]).intersection(set(pred_annots[i]))
        # print(type(pred_annots[i]), type(tp))
        fp = set(pred_annots[i]) - tp
        fn = set(real_annots[i]) - tp
        for go_id in sorted(fp):  # modification
            mi += go.get_ic(go_id)
        for go_id in sorted(fn):  # modification
            ru += go.get_ic(go_id)
        fps.append(fp)
        fns.append(fn)
        tpn = len(tp)
        fpn = len(fp)
        fnn = len(fn)
        total += 1
        recall = tpn / (1.0 * (tpn + fnn))
        r += recall
        if len(pred_annots[i]) > 0:
            p_total += 1
            precision = tpn / (1.0 * (tpn + fpn))
            p += precision

    # print(type(ru), type(mi))
    ru /= total
    mi /= total
    r /= total
    if p_total > 0:
        p /= p_total
    f = 0.0
    if p + r > 0:
        f = 2 * p * r / (p + r)
    # s = mpmath.sqrt(ru * ru + mi * mi)
    # s = np.sqrt(np.float64(ru) * np.float64(ru) + np.float64(mi) * np.float64(mi), dtype=np.float64)
    s = math.sqrt(ru * ru + mi * mi)
    return f, p, r, s, ru, mi, fps, fns


if __name__ == "__main__":
    main()
