import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix
from k_party import k_party

class n_party_states:
    def __init__(self):
        return

    '''
    It has maximal entanglement between A3A4 and B1B2 or between A3B1 and A4B2, while it is not reducible to a pair of Bell states. 
    The amount of entanglement between A3B2 and A4B1 has the value 1 when we use von Neumann entropy as an entanglement measure
    Ordering of qubits is A3,A4,B1,B2
    '''
    def four_party_gme(self):
        zeta_0 =  1/2 * (Statevector.from_label("0000") - Statevector.from_label("0011") - Statevector.from_label("0101") + Statevector.from_label("0110"))
        zeta_1 = 1/2 *  (Statevector.from_label("1001") + Statevector.from_label("1010") + Statevector.from_label("1100") + Statevector.from_label("1111"))
        return (1/np.sqrt(2)) * (zeta_0 + zeta_1)

    '''
    @ Unlockable_bound_entangled_state
    a four-party quantum state which cannot be written in a separable form 
    and from which no pure entanglement can be distilled by LOCC among the parties, 
    and yet when any two of the parties come together in the same laboratory 
    they can perform a measurement which enables the other two parties to create a pure maximally entangled state
    between them without coming together
    '''
    def unlockable_bound_entangled_state(self):
        phi_plus = 1/np.sqrt(2)* (Statevector.from_label("00") + Statevector.from_label("11"))
        phi_minus = 1/np.sqrt(2)* (Statevector.from_label("00") - Statevector.from_label("11"))

        psi_plus = 1/np.sqrt(2)* (Statevector.from_label("01") + Statevector.from_label("10"))
        psi_miuns = 1/np.sqrt(2)* (Statevector.from_label("01") - Statevector.from_label("10"))

        phi_plus_dm = DensityMatrix(np.outer(phi_plus.data, phi_plus.data.conj()))
        phi_minus_dm = DensityMatrix(np.outer(phi_minus.data, phi_minus.data.conj()))
        psi_plus_dm = DensityMatrix(np.outer(psi_plus.data, psi_plus.data.conj()))
        psi_minus_dm = DensityMatrix(np.outer(psi_miuns.data, psi_miuns.data.conj()))

        ube_state = (1/4) * (phi_plus_dm.tensor(phi_plus_dm) + phi_minus_dm.tensor(phi_minus_dm) + psi_plus_dm.tensor(psi_plus_dm) + psi_minus_dm.tensor(psi_minus_dm))
        return ube_state


    '''
    Generate five party and six party Absolutely maximally entangled states (AME)
    Specifically AME(5,2) and AME(6,2) where (n,d) is the (number of parties, qudit_dimension)    
    '''

    def five_party_ame_0(self):
        ame = (1/4) * (Statevector.from_label("00000") + Statevector.from_label("10010") + Statevector.from_label("01001") + Statevector.from_label("10100")
        + Statevector.from_label("01010") - Statevector.from_label("11011") - Statevector.from_label("00110") - Statevector.from_label("11000")
        - Statevector.from_label("11101") - Statevector.from_label("00011") - Statevector.from_label("11110") - Statevector.from_label("01111")
        - Statevector.from_label("10001") - Statevector.from_label("01100") - Statevector.from_label("10111") + Statevector.from_label("00101"))
        return ame

    def five_party_ame_1(self):
        ame = (1/4) * (Statevector.from_label("11111") + Statevector.from_label("01101") + Statevector.from_label("10110") + Statevector.from_label("01011")
        + Statevector.from_label("10101") - Statevector.from_label("00100") - Statevector.from_label("11001") - Statevector.from_label("00111")
        - Statevector.from_label("00010") - Statevector.from_label("11100") - Statevector.from_label("00001") - Statevector.from_label("10000")
        - Statevector.from_label("01110") - Statevector.from_label("10011") - Statevector.from_label("01000") + Statevector.from_label("11010"))
        return ame

    #AME(6,2)
    def six_party_ame(self):
        ame = np.sqrt(1/2) * (Statevector.from_label("0").tensor(self.five_party_ame_0()) + Statevector.from_label("1").tensor(self.five_party_ame_1()))
        return ame
        

#test function
def test_bipartition_entropy(n, k_party_obj):
    for i in range(0, n):
        for j in range(i+1, n):
            print("i = ", i)
            print("j = ", j)
            # em.get_le_upper_bound(k_party_obj, i, j)
            # em.get_le_lower_bound(k_party_obj, i, j)
            A = set([i,j])
            B = set(np.arange(n))

            # Get new set with elements that are only in a but not in b
            B = B.difference(A)
            print("A = ", A, " B = ", B)
            ee = k_party_obj.bipartite_entropy(list(A), list(B))
            print('EE = ', ee)

    return

def test():
    nps = n_party_states()
    fps = nps.four_party_gme()
    print("fps = ", fps)
    print("is valid = ", fps.is_valid())

    ube_state = fp.unlockable_bound_entangled_state()
    spe1 = nps.five_party_ame_0()
    spe2 = nps.five_party_ame_1()
    spe3 = nps.six_party_ame()

    #print("ube_state = ", ube_state)
    print("spe = ", spe1)
    print("spe = ", spe2)
    print("spe = ", spe3)

    print("is valid = ", spe1.is_valid())
    print("is valid = ", spe2.is_valid())
    print("is valid = ", spe3.is_valid())

    n = 5
    k_party_obj = k_party(5, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2])], spe1)
    test_bipartition_entropy(n, k_party_obj)

    n = 6
    k_party_obj = k_party(6, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2])], spe3)
    test_bipartition_entropy(n, k_party_obj)