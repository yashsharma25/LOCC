import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit.quantum_info import shannon_entropy
from scipy.linalg.misc import norm


class k_party:
    '''
    k is the number of parties

    state_desc is an array of 2-tuples where first entry is no. of qudits each party has
    and second entry is the dimension of each qudit
    
    Size of array state_desc = k

    Example:[(2, [3, 3]), (4, [2,2,2,2]), (1, [2])]

    Here party A has 2 qutrits, party B has 4 qubits, party C has 1 qubit
    '''

    #qState can be a statevector, densityMatrix, quantumCircuit or graph state. All 4 descriptions will be supported
    def __init__(self, k, dims, state_desc, q_state):
        #all the qudits will be intialised as |0>
        self.k = k
        self.dims = dims
        self.parties = k
        self.state_desc = state_desc
        self.q_state = q_state

    #get the Hilbert space dimension of the k-party state
    def dims(self):
        return self.dims

    #get hilbert space dimension of the specified party
    def get_dims_by_party(self, party_index):
        if party_index > self.k:
            return "Party index out of bounds"
        
        #Are all the qudits that a party has kept separately? Or is it one state?
        return max(self.state_desc[party_index][1])


    #get total qudits in the k_party state
    def total_qudits(self):
        total_qudits = 0
        for s in self.state_desc:
            total_qudits += s[0]

        return total_qudits

    '''
    Input: party index
    Output: An index range of the qudits the specified party holds
    '''
    def get_qudit_index_range(self, party_index):
        qudits_before = 0
        for index, s in enumerate(self.state_desc):
            if index != party_index:
                qudits_before += s[0]

            else:
                break

        return list(range(qudits_before, qudits_before + self.state_desc[party_index][0]))

    #creates a copy of the current k_party state
    def copy(self):
        return

    #new_party_desc is a tuple (number_of_qudits, dims of each qudit)
    def add_new_party(self, new_party_desc):
        self.k += 1
        self.state_desc.append(new_party_desc)

    #will return density matrix of the k-party state
    def get_density_matrix(self):
        return

    #will return statevector of the k-party state
    def get_statevector(self):
        return

    # will return reduced density matrix of the specified party(by tracing out all other parties)
    def get_reduced_density_matrix(self, party_index):
        return

    def is_transformable(self, other_k_party_state):
        #if condition satisfies
        #return True

        return False

    #apply a local operation on a specific party
    #Will apply to all qudits specified (of the specified party)
    def local_operation(self, party_index, qudit_indices, unitary_operator):
        return

    #measure the i'th qudit of the  j'th party
    #update the state afte measurement
    #projective measurement
    def measure(self, party_index, qudit_indices):
        self.q_state.measure(party_index)

    def measure_different_basis(self, party_index, qudit_indices, basis_matrix):
        self.q_state.evolve(basis_matrix)
        self.measure(party_index, qudit_indices)
        
    #return the probability by which a state is transformable to another using LOCC
    #SLOCC = Stochastic LOCC
    def slocc_equivalence(self, other_k_party_state):
        probability = 0.0
        return probability

    #check if a k_party state can be transformed trivially into another k_party state
    #trivially means just by applying local unitary operations
    def lu_equivalence(self, other_k_party_state):
        return False

    #check if two k_party states are locally clifford equivalent
    def lc_equivalence(self, other_k_party_state):
        return False
    
    def measure_all_possible_posteriors_qiskit(self, qubit_to_measure):
        outcomes = []
        all_possible_posteriors = []

        while len(outcomes) < self.dims:
        
            outcome, state = self.q_state.measure([qubit_to_measure])
            if outcome not in outcomes:
                outcomes.append(outcome)
                prob = self.q_state.probabilities([qubit_to_measure])[int(outcome)]
                all_possible_posteriors.append((state.data, prob))

        return all_possible_posteriors

    def entanglement_entropy(self):
        return self.E.entropy_using_singular_values(self.q_state)

    def entanglement_entropy_for_state(self, state):
        u, singular_values, vT = np.linalg.svd(state)

        squared_singular_vals = np.square(singular_values)

        #shannon_entropy accepts a probability vector as input
        #singular values sum up to 1 and all elements are >= 0 so it is a probability vector
        entanglement_entropy = shannon_entropy(squared_singular_vals, base=2)

        return entanglement_entropy