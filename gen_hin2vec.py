"""
Generate the input data for hin2vec

Author: Zeyu Li
"""

import os
import sys
import pandas as pd
try:
    import _Pickle as pickle
except:
    import pickle

DATA_DIR = "./data/"


def read_file(ds, lp):
    """
    ds: dataset
    lp: link prediction (bool)

    id2type: list
    edges: numpy.array
    """

    # load type file
    with open(DATA_DIR + "{}.type".format(dataset), "rb") as fin:
        id2type = pickle.load(fin)

    # lp = 1, separate train/test
    if lp:
        fname = DATA_DIR + "{}.edges.lp.train".format(dataset)
    else:
        fname = DATA_DIR + "{}.edges".format(dataset)

    edges = pd.read_csv(fname, header=None, sep="\t")
    edges = edges.values

    return id2type, edges


def build_input_file(id2type, edges):
    output_dir = "HIN2VEC_DATA"
    if os.path.isdir(output_dir):
        os.mkdir(output_dir)
    with open(output_dir + "hin2vec_edges", "w") as fout:
        n_edge = edges.shape[0]
        for i in range(n_edge):
            u1, u2 = n_edge[i][0], n_edge[i][1]
            tu1, tu2 = id2type[u1], id2type[u2]
            line = "{}\t{}\t{}\t{}\t{}-{}".format(
                u1, tu1, u2, tu2, tu1, tu2)
            rev_line = "{}\t{}\t{}\t{}\t{}-{}".format(
                u2, tu2, u1, tu1, tu2, tu1)
            print(line, file=fout)
            print(rev_line, file=fout)


if __name__ == "__main__":
    if len(sys.argv) <  1 + 2:
        print("[dataset] [lp]")
    dataset = sys.argv[1]
    lp = int(sys.argv[2])
    assert dataset in ["movielens", "yelp", "dbis"], "invalid dataset"

    print("reading file ...")
    i2t, edges = read_file(dataset, lp)

    print("building + writing ...")
    build_input_file(i2t, edges)

    print("Done!")


