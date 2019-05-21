"""
generating path by JUST
"""

import os, sys
import random
from collections import deque
import pickle
from multiprocessing import Pool
from tqdm import tqdm

DATA_DIR = os.getcwd() + "/data/"
DUMP_DIR = os.getcwd() + "/just_walk/"

def just_walk(G, 
              node_type, 
              node_nbr_cnt, 
              alpha, 
              start_node, 
              wlen, 
              qlen):
    """
    node_type:
    start_node: int
    """

    walk = [start_node]
    dq = deque(maxlen=qlen)

    cur_len = 1
    cur_node = start_node
    cur_type = node_type[cur_node]

    all_types = list(set(node_type))

    def stay(cl):
        homo_nodes = G[cur_node][cur_type]
        next_node = random.choice(list(homo_nodes))
        cl += 1
        walk.append(next_node)
        dq.append(cur_type)
        return next_node, cl
    
    def jump(cl):
        tmp_next_type_list = list(set(all_types) - set(dq))
        next_type = random.choice(tmp_next_type_list)
        loop_time = 0
        while len(G[cur_node][next_type]) == 0:
            next_type = random.choice(tmp_next_type_list)
            loop_time += 1
            if loop_time > 3:
                tmp_next_type_list = all_types

        next_node = random.choice(list(G[cur_node][next_type]))

        cl = 1
        walk.append(next_node)
        dq.append(next_type)
        return next_node, cl
        
    while len(walk) < wlen:
        cur_type = node_type[cur_node]

        # P_stay = 0.0
        if len(G[cur_node][cur_type]) == 0:
            next_node, cur_len = jump(cur_len)

        # P_stay = 1.0
        elif node_nbr_cnt[cur_node] == len(G[cur_node][cur_type]):
            next_node,cur_len = stay(cur_len)

        # P_stay = alpha ** cur_len
        else:
            if random.random() > alpha ** cur_len:
                next_node, cur_len = jump(cur_len)
            else:
                next_node, cur_len = stay(cur_len)

        cur_node = next_node
    return " ".join(str(x) for x in walk)


def main(dataset, full_graph, alpha, qlen, cvg, wlen, multiproc):

    # ===============
    # Load Node Types 
    # ===============

    with open(DATA_DIR + "{}.type".format(dataset), "rb") as fin:
        node_types = pickle.load(fin)
    all_types = list(set(node_types))
    print("\t- [Loading node type: Done!]")

    # ============================
    # Load Edges, Build Network
    # ============================

    type_nbrs = {}
    node_nbr_cnt = {}
    type_nodes = dict(zip(all_types, [set() for _ in range(len(all_types))]))

    dataset_suffix = "" if full_graph else ".lp.train" 
    with open(DATA_DIR + "{}.edges{}".format(dataset, dataset_suffix), "r") as fin:
        for line in fin.readlines():
            id1, id2 = [int(x) for x in line.strip().split("\t")]
            type1 = node_types[id1]
            type2 = node_types[id2]
            if id1 not in type_nbrs:
                type_nbrs[id1] = dict(zip(all_types, [set() for _ in range(len(all_types))]))
            if id2 not in type_nbrs:
                type_nbrs[id2] = dict(zip(all_types, [set() for _ in range(len(all_types))]))
            
            type_nbrs[id1][type2].add(id2)
            type_nbrs[id2][type1].add(id1)
            type_nodes[type1].add(id1)
            type_nodes[type2].add(id2)

            node_nbr_cnt[id1] = node_nbr_cnt.get(id1, 0) + 1
            node_nbr_cnt[id2] = node_nbr_cnt.get(id2, 0) + 1
        
    print("\t- [Building graph: Done!]")
    
    # ====================
    # Generate Random Walk
    # ====================

    print("\t- Generating walks ...")

    rand = random.Random(2019)
    walks = []
    
    init_node_list = list(type_nbrs.keys())

    async_results = []

    if multiproc > 1:
        cvg_per_process = cvg // multiproc
        pool = Pool(processes=multiproc)

        for i in range(multiproc):
            res = pool.apply_async(worker, 
                                   args=(type_nbrs, 
                                         node_types,
                                         node_nbr_cnt,
                                         init_node_list, 
                                         alpha,
                                         cvg_per_process,
                                         wlen,
                                         qlen))

            async_results.append(res)

        pool.close()
        pool.join()

        for r in async_results:
            walks += r.get()

    else:
        for _ in tqdm(range(cvg)):  # Iterate the node set for cnt times
            rand.shuffle(init_node_list)
            for i, init_node in enumerate(init_node_list):
                walks.append(
                        just_walk(
                            G=type_nbrs,
                            node_type=node_types,
                            node_nbr_cnt=node_nbr_cnt,
                            alpha=alpha,
                            start_node=init_node, 
                            wlen=wlen, 
                            qlen=qlen))
                if i % 500 == 0:
                    print("{:.02f}".format(i/len(init_node_list)))
    print("\t\tNumber of walks generated :", end=" ")
    print(len(walks))

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

def worker(G, 
           node_type,
           node_nbr_cnt,
           init_node_list, 
           alpha,
           cvg, 
           len_walk, 
           len_queue):

    rand = random.Random(2019)
    per_walks = []
    for _ in range(cvg):  # Iterate the node set for cnt times
        rand.shuffle(init_node_list)
        for init_node in init_node_list:
            per_walks.append(
                    just_walk(
                        G, 
                        node_type=node_type,
                        node_nbr_cnt=node_nbr_cnt,
                        alpha=alpha,
                        start_node=init_node, 
                        wlen=len_walk, 
                        qlen=len_queue))
            # print(per_walks[-1])
    return per_walks


if __name__ == "__main__":
    if len(sys.argv) < 1 + 7:
        print("Usage:\npython {} ".format(sys.argv[0]) 
              + "[dataset] [full_graph] [alpha] [q length]"
              + "[coverage] [walk length] [multiproc]" )
        sys.exit(0)
    
    dataset = sys.argv[1]
    full_graph = True if int(sys.argv[2]) == 1 else False
    alpha = float(sys.argv[3])
    qlen = int(sys.argv[4])
    cvg = int(sys.argv[5])
    wlen = int(sys.argv[6])
    multiprocess = int(sys.argv[7])

    main(dataset, full_graph, alpha, qlen, cvg, wlen, multiprocess) 


