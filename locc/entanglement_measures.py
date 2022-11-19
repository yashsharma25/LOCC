#We might probably merge this class with the measures.py class that qiskit already has
import numpy as np
import math
from qiskit.quantum_info import shannon_entropy
from scipy import optimize

from scipy.linalg import expm
from k_party import k_party


class EntanglementMeasures:
    def __init__(self, N, psi, party_to_measure):
        self.k_party_obj = None
        self.N = N
        self.psi = psi
        self.party_to_measure = party_to_measure

    def entanglement_entropy(self, quantum_state):
        return

    def entanglement_length(self, quantum_state):
        return

    def entanglement_fluctuation(self, quantum_state):
        return

    #lower bound for localisable entanglement
    def get_le_lower_bound(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj
        self.psi = self.k_party_obj.q_state

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, 4)
        res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                        options={'xatol': 1e-8, 'disp': True})
        print("Entanglement entropy = ", res.fun)
        return res.fun

    #upper bound for localisable entanglement
    def get_le_upper_bound(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj

        self.psi = self.k_party_obj.q_state
        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, 4)
        res = optimize.minimize(self.maximise_le, v, method='nelder-mead',
                        options={'xatol': 1e-8, 'disp': True})
        print("Entanglement entropy = ", -1 * res.fun)
        return -1 * res.fun

    def nursing_index(self, quantum_state,  partyA, partyB):
        return

    def entropy_using_singular_values(self, state):
        u, singular_values, vT = np.linalg.svd(state)

        squared_singular_vals = np.square(singular_values)

        #shannon_entropy accepts a probability vector as input
        #singular values sum up to 1 and all elements are >= 0 so it is a probability vector
        entanglement_entropy = shannon_entropy(squared_singular_vals, base=2)

        return entanglement_entropy

    def von_neuman_entropy(self, rho):
        eigen_values = np.linalg.eigvals(rho)

        # Drop zero eigenvalues so that log2 is defined
        my_list = [x for x in eigen_values.tolist() if x.real > 0]
        eigen_values = np.array(my_list)
        #print("Eigen values = ", eigen_values)

        entropy = 0

        for ev in eigen_values:
            #print("Eigen value = ", ev.real)
            #print("Entropy = ", ev.real * math.log2(ev.real))
            entropy += ev * math.log2(ev.real)

        entropy *= -1
        return entropy

    #by using the -tr(rho log rho)
    def von_neumann_entropy_using_trace(rho):
        R = rho * (np.linalg.logm(rho) / np.linalg.logm(np.matrix([[2]])))
        S = -np.matrix.trace(R)
        return S

    
    def minimise_le(self, v):
        self.psi = self.k_party_obj.q_state

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

        # if (self.party_to_measure == 2):
        #     m = np.kron(np.kron(np.eye(self.N), np.eye(self.N)), U)

        # elif (self.party_to_measure == 1):
        #     m = np.kron(np.kron(np.eye(self.N), U), np.eye(self.N))

        # elif (self.party_to_measure == 0):
        #     m = np.kron(np.kron(U, np.eye(self.N)), np.eye(self.N))

        # self.psi = m @ self.psi.flatten()

        # self.psi = self.psi.reshape((self.N, self.N, self.N))

        #measure
        self.psi = self.psi.evolve(U, [self.party_to_measure])
        q = k_party(self.k_party_obj.k, self.N, None, self.psi)
        q.measure_all_possible_posteriors_qiskit(self.party_to_measure)
        
        entropies = []
        probabilities = []
        posteriors = []

        for state in q.all_possible_posteriors:
            if (self.party_to_measure == 0):
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N ** 2, self.N)))
                posteriors.append(state[0].reshape(self.N,  self.N ** 2))


            else:
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N , self.N ** 2)))
                posteriors.append(state[0].reshape(self.N ** 2,  self.N))
                
            probabilities.append(state[1])

        #compute weighted average
        avg_entropy = np.dot(probabilities, entropies)
        return avg_entropy


    def maximise_le(self, v):
        self.psi = self.k_party_obj.q_state

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

        #measure
        self.psi = self.psi.evolve(U, [self.party_to_measure])
        q = k_party(self.k_party_obj.k, self.N, None, self.psi)
        q.measure_all_possible_posteriors_qiskit(self.party_to_measure)
        
        entropies = []
        probabilities = []
        posteriors = []

        for state in q.all_possible_posteriors:
            if (self.party_to_measure == 0):
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N ** 2, self.N)))
                posteriors.append(state[0].reshape(self.N,  self.N ** 2))

            else:
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N , self.N ** 2)))
                posteriors.append(state[0].reshape(self.N ** 2,  self.N))
                
            probabilities.append(state[1])

        #compute weighted average
        avg_entropy = np.dot(probabilities, entropies)
        return -1 * avg_entropy