from scipy.linalg import svdvals
from scipy.stats import entropy
from scipy.sparse.linalg import svds
from scipy.linalg import expm, sinm, cosm
from example_ghz import GHZ

import numpy as np

class optimiser:
    def __init__(self, N, psi):
        self.N = N
        self.psi = psi

    def compute_nursing_index(self, v):
        self.psi = self.psi
        M = np.zeros((self.N, self.N), dtype = complex)
        for i in range(0,  self.N):
            M[i][i] = v[i]
        
        vector_index = self.N
        for row in range(0,  self.N - 1):
            for column in range(row + 1,  self.N):
                M[row][column] = v[vector_index] + 1j * v[vector_index+1]
                M[column][row] = v[vector_index] - 1j * v[vector_index+1]
                vector_index += 2

        U = expm(1j * M)

        m = np.kron(np.eye(self.N), np.eye(self.N))

        m = np.kron(m, U)

        #measure Charlie's qubit
        self.psi = m @ self.psi.flatten()

        self.psi = self.psi.reshape((self.N, self.N, self.N))

        #measure
        self.measure_all_possible_posteriors(2)
        
        entropies = []
        probabilities = []
        posteriors = []

        for state in q.all_possible_posteriors:
            entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N, self.N**2)))
            probabilities.append(state[1])
            posteriors.append(state[0].reshape(self.N,  self.N ** 2))
        #print("Entropies = ", r.entropies)

        #compute weighted average
        avg_entropy = np.dot(probabilities, entropies)
        #print(-1 * avg_entropy)
        return -1 * avg_entropy

    def generate_unitary(self, v):
        M = np.zeros((N,N), dtype = complex)
        for i in range(0, N):
            M[i][i] = v[i]
        
        #first N elements are diagonal elements, hence start from Nth index 
        vector_index = N
        for row in range(0, N-1):
            #take care of the element and its conjugate transpose
            #only run over the upper triangular
            for column in range(row + 1, N):
                M[row][column] = v[vector_index] + 1j * v[vector_index+1]
                M[column][row] = v[vector_index] - 1j * v[vector_index+1]
                vector_index += 2
       
        U = expm(1j * M)
        return U

opt = optimiser(3, GHZ(3))
opt.compute_nursing_index(np.random.uniform(0, 2*np.pi, 9))