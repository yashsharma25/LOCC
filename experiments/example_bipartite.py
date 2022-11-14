#gets qutrit states phi and psi, checks if psi is transformable to phi

import numpy as np
from locc.utils import get_density_matrix, partial_trace, majorisation

ket0 = [1, 0, 0]
ket1 = [0, 1, 0]
ket2 = [0, 0, 1]

def main():
    psi = np.sqrt(1/2) * np.kron(ket0, ket0) + np.sqrt(2/5)  * np.kron(ket1, ket1)  + np.sqrt(1/10) * np.kron(ket2, ket2)
    phi = np.sqrt(3/5) * np.kron(ket0, ket0) + np.sqrt(1/5)  * np.kron(ket1, ket1)  + np.sqrt(1/5) * np.kron(ket2, ket2)

    d_psi = get_density_matrix(psi)
    d_phi = get_density_matrix(phi)

    d_psi = d_psi.reshape([3,3,3,3])
    d_phi = d_phi.reshape([3,3,3,3])

    reduced_psi = partial_trace(d_psi)
    reduced_phi = partial_trace(d_phi)


    is_transformable = majorisation(reduced_psi, reduced_phi)
    print(is_transformable)


main()