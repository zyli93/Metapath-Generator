# Metapath guided random walk generator

Zeyu Li <zyli@cs.ucla.edu>

### Run 

```
$ python3 gene_walk.py [dataset] [full_graph] [length_of_walk] [coverage] [multiprocessing]
```

or using the other version that implemented by dictionary instead of `networkx`.

```
$ python3 gene_walk_dict.py [dataset] [full_graph] [length_of_walk] [coverage] [multiprocessing]
```
The latter runs faster.

The parameters are the following:
- __dataset__: the name of the dataset
- __full_graph__: when 1, using full graph, otherwise use `[dataset].edges.lp.train` for link prediction
- __length_of_walk__: length of the walk, metapath2vec set it to 100
- __coverage__: the `numwalks` parameters, the number of times each node was covered 
- __multiprocessing__: the number of processes to run the generation. 


### Input

1. `[dataset].edges`: id pairs of edges. [plain txt]
2. `[dataset].type`: a pickle dumpped file in this form - `[id1_type, id2_type, ...]`. Type is represented by char, such as `A`. [binary]
3. `[dataset].edge.lp.train`: subgraph for training of link prediction [plain text]
4. `[dataset].metapath`: a set of metapath separated by `\n`. [plain text]
