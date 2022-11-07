import qiskit
from qiskit import QuantumCircuit

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
    def __init__(self, k, state_desc, qState):
        #all the qudits will be intialised as |0>
        return

    #get the Hilbert space dimension of the k-party state
    def dims(self):
        return

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
        return

    #return the probability by which a state is transformable to another using LOCC
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