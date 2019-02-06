import os, sys
import pickle

INPUT_DIR = "./data/"
OUTPUT_DIR = "./pte_data/"

# yelp_type = ['B', 'C', 'L', 'U']  # BC, BU, BL
yelp_type = ['B', 'U']  
yelp_net = ["UU", "UB"]

# movielens_type = ['A', 'D', 'M', 'U']  # MA, MD, MU
movielens_type = ['A', 'D', 'M', 'U']  # MA, MD, MU
movielens_net = ['MA', 'MD', 'MU']  # MA, MD, MU

# dbis_type = ['A', 'P', 'V']
dbis_type = ['A', 'P']
dbis_net = ['AP']

dataset_net = {
    "yelp": (yelp_net, yelp_type, "U"),
    "movielens": (movielens_net, movielens_type, "M"),
    "dbis": (dbis_net, dbis_type, "A")
}

def main(dataset, full_graph):
    with open(INPUT_DIR + "{}.type".format(dataset), "rb") as fin:
        type_list = pickle.load(fin)

    dataset_suffix = ".lp.train" if not full_graph else ""

    net_edge, ent, interest_ent = dataset_net[dataset]

    with open(INPUT_DIR + "{}.edges{}".format(dataset, dataset_suffix), "r") as fin, \
        open(OUTPUT_DIR + "{}.net{}".format(dataset, dataset_suffix), "w") as fout_net:

        for line in fin.readlines():
            id1, id2 = [int(x) for x in line.strip().split("\t")]
            type1, type2 = type_list[id1], type_list[id2]

            type_str = "".join([type1, type2])

            if type_str in net_edge:
                fout_net.write(
                    "{} {} {} {}\n".format(id1, id2, 1, "w")
                )
            elif type_str[::-1] in net_edge:
                fout_net.write(
                    "{} {} {} {}\n".format(id2, id1, 1, "w")
                )

           # if type_str or type_str[::-1] in net_edge:
           #     fout_net.write(
           #         "{} {} {} {}\n".format(id1, id2, 1, "w")
           #     )

    # print(ent)
    # print(interest_ent)

    with open(OUTPUT_DIR + "{}.node{}".format(dataset, dataset_suffix), "w") as fout_node, \
        open(OUTPUT_DIR + "{}.word{}".format(dataset, dataset_suffix), "w") as fout_word:
        
        for i, t in enumerate(type_list):
            if t in ent:
                fout_node.write("{}\n".format(i))
                if t == interest_ent:
                    fout_word.write("{}\n".format(i))

if __name__ == "__main__":
    if len(sys.argv) < 1 + 2:
        print("Usage:\npython {} [dataset] [full_graph] [type] [node]".format(sys.argv[0]))
        sys.exit(0)
    
    ataset = sys.argv[1]
    full_graph = True if int(sys.argv[2]) == 1 else False

    main(dataset, full_graph)
    


