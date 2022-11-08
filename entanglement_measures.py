#We might probably merge this class with the measures.py class that qiskit already has
import numpy as np
import math
from qiskit.quantum_info import shannon_entropy


class EntanglementMeasures:
    def entanglement_entropy(self, quantum_state):
        return

    def entanglement_length(self, quantum_state):
        return

    def entanglement_fluctuation(self, quantum_state):
        return

    #lower bound for localisable entanglement
    def get_le_lower_bound(self):
        return

    #upper bound for localisable entanglement
    def get_le_upper_bound(self):
        return

    def nursing_index(self):
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