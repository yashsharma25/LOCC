class kParty:
    '''
    k is the number of parties

    state_desc is an array of 2-tuples where first entry is no. of qudits each party has
    and second entry is the dimension of each qudit
    
    Size of array state_desc = k

    Example:[(2, [3, 3]), (4, [2,2,2,2]), (1, [2])]

    Here party A has 2 qutrits, party B has 4 qubits, party C has 1 qubit
    '''

    #qState can be a statevector, densityMatrix or graph state. All 3 descriptions will be supported
    def __init__(self, k, state_desc, qState):
        #all the qudits will be intialised as |0>
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