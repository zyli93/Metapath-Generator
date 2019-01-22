import os, sys
import pickle
DATA_DIR = "./data/"
REFROM_DATA_DIR = "./hin_data/"

def main(dataset, full_graph):
    data_suffix = "" if full_graph else ".lp.train"
    with open(DATA_DIR + "{}.type".format(dataset), "rb") as fin:
        type_list = pickle.load(fin)

    with open(DATA_DIR + "{}.edges{}".format(dataset, data_suffix), "r") as fin, \
        open(DATA_DIR + "{}.hin_edges{}".format(dataset, data_suffix), "w") as fout: 
        for line in fin.readlines():
            id1, id2 = [int(x) for x in line.strip().split(" ")]
            type1, type2 = type_list[id1], type_list[id2]
            direction1 = "{:d}\t{}\t{:d}\t{}\t{}\n".format(id1, type1, id2, type2, "N")
            direction2 = "{:d}\t{}\t{:d}\t{}\t{}\n".format(id2, type2, id1, type1, "N")
            fout.write(direction1)
            fout.write(direction2)

if __name__ == "__main__":
    if len(sys.argv) != 1 + 2:
        print("Usage {} [dataset] [full_graph]".format(sys.argv[0]))
        sys.exit(1)

    if not os.path.isdir(REFROM_DATA_DIR):
        os.mkdir(REFROM_DATA_DIR)
    
    dataset = sys.argv[1]
    full_graph = True if int(sys.argv[2]) == 1 else False

    main(dataset, full_graph)