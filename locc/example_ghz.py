from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures

def GHZ(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten())

    print(ghz)
    return psi
    #print("Norm of state =", norm(psi.flatten()))

#now we compute the nursing numbers for this state

em = EntanglementMeasures(2, GHZ(2), 2)
em.get_le_upper_bound(GHZ(2), 0, 1)
