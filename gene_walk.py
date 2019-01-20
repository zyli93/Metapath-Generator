import os, sys
import pickle
import random
import networkx as nx
from tqdm import *
import multiprocessing as mp

DATA_DIR = os.getcwd() + "/data/"
DUMP_DIR = os.getcwd() + "/metapath/"

def get_typed_nodes(G, type=None):
    """ Get specific type or all nodes of nodelist in the graph

    Args:
        type - The entity type of the entity.
                If set as `None`, then all types of nodes would be returned.

    Return:
        nodelist - the list of node with `type`
    """
    if not G.number_of_edges() or not G.number_of_nodes():
        sys.exit("Graph should be initialized before get_nodelist()!")

    if not type:
        return list(G.nodes)
    return [node for node in list(G.nodes)
            if node[0] == type]

def meta_path_walk(G, 
                   start, 
                   len_walk,
                   alpha=0.0, 
                   pattern=None):
    """Single Walk Generator

    Generating a single random walk that follows a meta path of `pattern`

    Args:
        rand - an random object to generate random numbers
        start - starting node
        alpha - probability of restarts
        pattern - (string) the pattern according to which to generate walks
        walk_len - (int) the length of the generated walk

    Return:
        walk - the single walk generated

    """
    def type_of(node_id):
        return node_id[0]

    rand = random.Random()
    # Checking pattern is correctly initialized
    if not pattern:
        sys.exit("Pattern is not specified when generating meta-path walk")

    pat_ind = 1
    walk = [start]
    cur_node = start

    # Generating meta-paths
    while len(walk) <= len_walk or pat_ind != len(pattern):

        # Updating the pattern index
        pat_ind = pat_ind if pat_ind != len(pattern) else 1

        # Decide whether to restart
        if rand.random() >= alpha:
            # Find all possible next neighbors
            possible_next_node = [neighbor
                                  for neighbor in G.neighbors(cur_node)
                                  if type_of(neighbor) == pattern[pat_ind]]
            # Random choose next node
            try:
                next_node = rand.choice(possible_next_node)
            except:
                print("pattern", pattern)
                print("pat_ind", pat_ind)
                print("pattern[pat_ind]", pattern[pat_ind])
                print("cur_node", cur_node)
                print("possible_next_node", possible_next_node)
                print("walk", walk)
                return " ".join(walk)
                # sys.exit()
        else:
            next_node = walk[0]

        walk.append(next_node)
        cur_node = next_node
        pat_ind += 1

    return " ".join(walk)

def main(dataset, len_walk, cvg, use_full):

    # =============
    # Load Metapath
    # =============
    dataset_suffix = "" if use_full else ".lp.train" 
    with open(DATA_DIR + 
              "{}.metapath{}".format(dataset, dataset_suffix), "r") as fin:
        metapaths = [x.strip() for x in fin.readlines()]

    # ===============
    # Load Node Types 
    # ===============

    with open(DATA_DIR + "{}.type".format(dataset), "rb") as fin:
        node_types = pickle.load(fin)
    print("\t- [Loading node type: Done!]")

    # ============================
    # Load Edges, Build Network
    # ============================

    G = nx.Graph()
    edges_list = []

    with open(DATA_DIR + "{}.edges".format(dataset), "r") as fin:
        for line in fin.readlines():
            id1, id2 = [int(x) for x in line.strip().split("\t")]
            node1 = node_types[id1] + "_" + str(id1)
            node2 = node_types[id2] + "_" + str(id2)
            edges_list.append([node1, node2]) 
        
    G.add_edges_from(edges_list)
    # print(G.nodes)

    print("\t- [Building graph: Done!]")
    
    # ====================
    # Generate Random Walk
    # ====================

    print("\t- Generating walks ...")

    rand = random.Random(2019)
    # walks = []

    for mp in metapaths:
        print("\t\t - now by MP-{}".format(mp))
        init_node_type = mp[0]
        init_node_list = get_typed_nodes(G, init_node_type)
        total = len(init_node_list)                

        walks = []

        if multiproc > 1:
            cvg_per_process = cvg // multiproc
            p = mp.Pool(process=multiproc)
            for i in range(multiproc):
                res = p.apply_async(worker, (G, init_node_list, cvg_per_process, ))
                walks += res
            p.close()
            p.join()

        else:
            for _ in tqdm(range(cvg)):  # Iterate the node set for cnt times
                rand.shuffle(init_node_list)
                for init_node in init_node_list:
                    walks.append(meta_path_walk(G, start=init_node, 
                                                len_walk=len_walk, pattern=mp))

    print("\t- [Generate walks: Done!]")
    
    # =======================
    # Dumping generated walks
    # =======================

    if not os.path.isdir(DUMP_DIR):
        os.mkdir(DUMP_DIR)
    
    with open(DUMP_DIR + 
              "{}.walks{}".format(dataset, dataset_suffix), "w") as fout:
        for walk in walks:
            fout.write(walk + "\n")
    
    print("\t- [Dumping walks: Done!]")
    print("Process Succeeded!")

def worker(G, init_node_list, cvg):
    walks = []
    for _ in range(cvg):  # Iterate the node set for cnt times
        rand.shuffle(init_node_list)
        for init_node in init_node_list:
            walks.append(meta_path_walk(G, start=init_node, 
                                        len_walk=len_walk, pattern=mp))
    return walks

if __name__ == "__main__":
    if len(sys.argv) != 1 + 5:  # TODO
        print("Invalid Parameters!")
        print("Usage:\n",
              "\tpython {} [path] [dataset] ".format(sys.argv[0]),
              "[full_graph] [length_of_walk] [coverage] [multiprocessing]")
        sys.exit(1)

    dataset = sys.argv[1]
    use_full = (int(sys.argv[2]) == 1)
    len_walk = int(sys.argv[3])
    cvg = int(sys.argv[4])
    multiproc = int(sys.argv[5])

    print("Metapath Generation:\n",
          "\tProcessing dataset: {}\n".format(dataset),
          "\tLength of Walk: {}, Coverage: {}".format(len_walk, cvg))

    main(dataset,
         len_walk,
         cvg,
         use_full,
         multiproc)    

