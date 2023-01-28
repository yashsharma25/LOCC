import numpy as np
from itertools import combinations
from qiskit.quantum_info import random_statevector
from k_party import k_party

class multiparty_solver:
    def __init__(self, N):
        self.N = N
        return

    def get_intervals(self):
        intervals = []
        for partition in ms.bipartitions():
            #check if partition is valid
            is_valid = True

            for node in partition[0]:
                if len(partition[0]) > 1:
                    if (node+1 not in partition[0]) and (node-1 not in partition[0]):
                        is_valid = False
            
            if is_valid:
                for node in partition[1]:
                    if len(partition[1]) > 1:
                        if (node+1 not in partition[1]) and (node-1 not in partition[1]):
                            is_valid = False


            if is_valid:
                intervals.append(partition)

        print(intervals)
        return intervals

    def bipartitions(self):
        for i in range(1, self.N):
            #the combinations function create all possible subsets of size i within the range n
            for comb in combinations(range(self.N), i):
                yield (set(comb), set(range(self.N)) - set(comb))


    def create_circular_graph(self):
        edges = []
        edge_ids = {}
        id = 0
        for v in range(self.N):
            edges.append((v, (v+1) % self.N))
            edge_ids[(v, (v+1) % self.N)] = id
            edge_ids[((v+1) % self.N, v)] = id
            id += 1

        print(edge_ids)
        return edges, edge_ids

    def compute_entropies_for_intervals(self, k_party_obj, edges, edge_ids, intervals):
        mat = np.zeros((len(intervals), len(intervals)))

        entropy_matrix = np.zeros((len(intervals), 1))
        for index, intvl in enumerate(intervals):
            print("Interval = ", intvl[0], intvl[1])
            for e in edges:
                if ((e[0] in intvl[0]) and (e[1] in intvl[1])) or ((e[1] in intvl[0]) and (e[0] in intvl[1])):
                    #now we know this is a crossing edge
                    #set this edgeId = 1 in the mat
                    mat[index][edge_ids[(e[0], e[1])]] = 1

            entropy_matrix[index] = k_party_obj.bipartite_entropy(list(intvl[0]), list(intvl[1]))


        print(mat)
        print("________________________")
        print(entropy_matrix)
      
        print("Shape of mat = ", mat.shape)
        print("Shape of entropy matrix = ", entropy_matrix.shape)

        p, res, rank, s = np.linalg.lstsq(mat, entropy_matrix)
        print(p)

ms = multiparty_solver(4)
intervals = ms.get_intervals()
edges, edge_ids = ms.create_circular_graph()
k_party_obj = k_party(4, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2])], random_statevector(16))
ms.compute_entropies_for_intervals(k_party_obj, edges, edge_ids, intervals)