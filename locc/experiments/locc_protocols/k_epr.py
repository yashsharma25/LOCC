import numpy as np
from .. import locc_operation
from sympy.physics.quantum.gate import H, X, Z
from k_party import k_party
from locc_controller import locc_controller

def generate_k_eprs(x_set, z_set, epr_set, k_party_obj):

    locc_ops = []
    #measure in computational basis
    for x in x_set:
        locc_ops.append(locc_operation(x, 0, "measure"))


    #measure in hadamard basis
    for z in z_set:
        #measure in hadamard basis
        locc_ops.append(locc_operation(z, 0, "default", np.array(H().get_target_matrix()).astype(np.float64)))
        locc_ops.append(locc_operation(z, 0, "measure"))

    k_epr_obj = locc_controller(locc_ops, k_party_obj)

    k_epr_obj.execute_protocol()

if __name__ == "__main__":
    x_set = [0, 1, 2]
    z_set = [3, 4, 5]
    epr_set = [6, 7, 8, 9]