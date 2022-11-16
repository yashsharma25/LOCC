from scipy.linalg import expm
from example_ghz import GHZ
from k_party import k_party
from scipy import optimize

import numpy as np

class optimiser:
    def __init__(self, N, psi, party_to_measure):
        self.N = N
        self.psi = psi
        self.party_to_measure = party_to_measure

    def compute_nursing_index(self, v):
        self.psi = self.psi

        #generate unitary matrix
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

        if (self.party_to_measure == 2):
            m = np.kron(np.kron(np.eye(self.N), np.eye(self.N)), U)

        elif (self.party_to_measure == 1):
            m = np.kron(np.kron(np.eye(self.N), U), np.eye(self.N))

        elif (self.party_to_measure == 0):
            m = np.kron(np.kron(U, np.eye(self.N)), np.eye(self.N))

        self.psi = m @ self.psi.flatten()

        self.psi = self.psi.reshape((self.N, self.N, self.N))

        #measure
        q = k_party(self.N, None, self.psi)
        q.measure_all_possible_posteriors(self.party_to_measure)
        
        entropies = []
        probabilities = []
        posteriors = []

        for state in q.all_possible_posteriors:
            entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N, self.N**2)))
            probabilities.append(state[1])
            posteriors.append(state[0].reshape(self.N,  self.N ** 2))

        #compute weighted average
        avg_entropy = np.dot(probabilities, entropies)
        return -1 * avg_entropy

opt = optimiser(2, GHZ(2), 2)
v = np.random.uniform(0, 2*np.pi, 4)
res = optimize.minimize(opt.compute_nursing_index, v, method='nelder-mead',
                options={'xatol': 1e-8, 'disp': True})
print("Entanglement entropy = ", -1 * res.fun)