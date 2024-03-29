import numpy as np
from itertools import combinations
from qiskit.quantum_info import random_statevector
from qiskit.quantum_info import Statevector
import networkx as nx
from k_party import k_party

class multiparty_solver:
    def __init__(self, N):
        self.N = N
        return

    def get_intervals(self):
        intervals = []
        
        for partition in ms.bipartitions():
            #check if partition is valid i.e if the interval is contigous
            #except the two cut vertices all other nodes should have both their neighbours in the same partition

            is_valid = True

            cut_vertices = 0
            if len(partition[0]) == 1 or len(partition[1]) == 1:
                is_valid = True

            else:
                for node in partition[0]:
                    neighbor_1 = node + 1
                    neighbor_2 = node - 1

                    if node == 0:
                        neighbor_2 = self.N - 1

                    elif node == self.N-1:
                        neighbor_1 = 0

                    if (neighbor_1 not in partition[0]) or (neighbor_2 not in partition[0]):
                        cut_vertices += 1

                        if cut_vertices > 2:
                            is_valid = False
                            break

                if is_valid:
                    cut_vertices = 0

                    for node in partition[1]:
                        neighbor_1 = node + 1
                        neighbor_2 = node - 1

                        if node == 0:
                            neighbor_2 = self.N - 1

                        elif node == self.N-1:
                            neighbor_1 = 0

                        if (neighbor_1 not in partition[1]) or (neighbor_2 not in partition[1]):
                            cut_vertices += 1

                            if cut_vertices > 2:
                                is_valid = False
                                break
                
            if is_valid:
                intervals.append(partition)

        #there are twice as many intervals generated because in the second half, just the order is flipped
        print("len(intervals) = ", len(intervals))
        # for i in intervals:
        #     print(i)
        list_half = round(len(intervals)/2)
        intervals = intervals[:list_half]
        return intervals

    def bipartitions(self):
        for i in range(1, self.N):
            #the combinations function create all possible subsets of size i within the range n
            for comb in combinations(range(self.N), i):
                yield (set(comb), set(range(self.N)) - set(comb))


    def create_complete_graph(self):
        G = nx.complete_graph(self.N)
        edge_ids = {}
        id = 0
        print("Num of edges = ", len(G.edges()))
        for e in G.edges():
            edge_ids[(e[0], e[1])] = id
            edge_ids[(e[1], e[0])] = id
            id += 1

        #print(edge_ids)
        return G.edges(), edge_ids

    '''
    Returns:
    A dictionary where the key is the two vertices of an edge, and the value is the weight
    '''
    def compute_entropies_for_intervals(self, k_party_obj, edges, edge_weights_maps, intervals):

        mat = np.zeros((len(intervals), len(edges)))

        entropy_matrix = np.zeros((len(intervals), 1))
        for index, intvl in enumerate(intervals):
            #print("Interval = ", intvl[0], intvl[1])
            for e in edges:
                if ((e[0] in intvl[0]) and (e[1] in intvl[1])) or ((e[1] in intvl[0]) and (e[0] in intvl[1])):
                    #now we know this is a crossing edge
                    #set this edgeId = 1 in the mat
                    mat[index][edge_weights_maps[(e[0], e[1])]] = 1

            entropy_matrix[index] = k_party_obj.bipartite_entropy(list(intvl[0]), list(intvl[1]))


        # print(mat)
        # print("________________________")
        # print(entropy_matrix)
      
        print("Shape of mat = ", mat.shape)
        print("Shape of entropy matrix = ", entropy_matrix.shape)

        weights, res, rank, s = np.linalg.lstsq(mat, entropy_matrix)
        #print(p)
        #return the edge weights and edge nodes
        for index, e in enumerate(edges):
            edge_weights_maps[(e[0], e[1])] = weights[index]
            edge_weights_maps[(e[1], e[0])] = weights[index]


        # for e in edge_weights_maps:
        #     print(e, edge_weights_maps[e])
        return weights
        
if __name__ == "__main__":
    ms = multiparty_solver(10)
    intervals = ms.get_intervals()
    edges, edge_ids = ms.create_complete_graph()
    k_party_obj = k_party(10, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2]),  (1, [2]), (1, [2])], random_statevector(2**10))

    ms.compute_entropies_for_intervals(k_party_obj, edges, edge_ids, intervals)