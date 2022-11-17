from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures
from k_party import k_party

def GHZ(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten())

    print(ghz)
    return psi
    #print("Norm of state =", norm(psi.flatten()))

#now we compute the nursing numbers for this state
k_party_obj = k_party(2, 2, None, GHZ(2))

em = EntanglementMeasures(2, GHZ(2), 2)
em.get_le_upper_bound(k_party_obj, 0, 1)
em.get_le_lower_bound(k_party_obj, 0, 1)
