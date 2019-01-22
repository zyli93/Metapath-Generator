import pickle
import sys

TYPE_DIR = "./data/"
INPUT_DIR = "./metapath/"
OUTPUT_DIR = "./typed_walk/"

target_type = ['v', 'i', 'f', 'a']

yelp_type = ['B', 'C', 'L', 'U']
movielens_type = ['B', 'C', 'L', 'U']
dbis_type = ['A', 'P', 'V']
aminer_type = ['A', 'P', 'V']

TYPE_MAP = {
    "yelp": dict(zip(yelp_type, target_type)),
    "movielens": dict(zip(movielens_type, target_type)),
    "dbis": dict(zip(dbis_type, target_type)),
    "aminer": dict(zip(aminer_type, target_type))
}

def main(dataset, full_graph):
    
    # Load type list
    with open(TYPE_DIR + "{}.type".format(dataset), "rb") as fin:
        type_list = pickle.load(fin)

    dataset_suffix = ".lp.train" if not full_graph else ""

    def pad_type(x):
        """string to string"""
        mapped_type = TYPE_MAP[dataset][type_list[int(x)]]
        return mapped_type + x 

    with open(INPUT_DIR + "{}.walks{}".format(dataset, dataset_suffix), "r") as fin, \
        open(OUTPUT_DIR + "{}.walks{}".format(dataset, dataset_suffix), "w") as fout:
        for line in fin.readlines():
            line_pad_type = [pad_type(x) for x in line.strip().split(" ")]
            fout.write(" ".join(line_pad_type) + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 1 + 2:
        print("Usage {} [dataset] [full_graph]".format(sys.argv[0]))
        sys.exit(1)
    
    dataset = sys.argv[1]
    full_graph = int(sys.argv[2])

    main(dataset, full_graph)