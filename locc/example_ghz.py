from qiskit.quantum_info import Statevector
import numpy as np

def GHZ(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten())

    print(ghz)
    return psi
    #print("Norm of state =", norm(psi.flatten()))

#now we compute the nursing numbers for this state