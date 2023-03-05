from qiskit.circuit.gate import Gate
from . import locc_controller
from . import locc_operation
from qiskit.quantum_info import Statevector, random_statevector
import numpy as np
from . import k_party
from sympy.physics.quantum.gate import H, X, Z

def teleportation(k_party_obj):

    locc_op1 = locc_operation(0, 0, "default", np.array(H().get_target_matrix()).astype(np.float64))
    locc_op2 = locc_operation(0, 0, "measure")
    locc_op3 = locc_operation(0, 1, "measure")
    locc_op4 = locc_operation(1, 0, "conditional_operation", np.array(X().get_target_matrix()), (0, 0, 1))
    locc_op5 = locc_operation(1, 0, "conditional_operation", np.array(Z().get_target_matrix()),  (0, 1, 1))

    locc_teleporation_obj = locc_controller([locc_op1, locc_op2, locc_op3, locc_op4, locc_op5], k_party_obj)

    locc_teleporation_obj.execute_protocol()

if __name__ == "__main__":
    #this will be shared by both alice and Bob
    bell_pair = 1/np.sqrt(2)* (Statevector.from_label("00") + Statevector.from_label("11"))

    #lets create a random state to be teleported
    psi = random_statevector(2)
    print("psi = ", psi)

    #lets create the k-party object (here k = 2)
    q_state = psi.tensor(bell_pair)
    k_party_obj = k_party(2, 2, [(2, [2, 2]), (1, [2])], q_state)

    print("Before protocol run k_party_obj =", k_party_obj.q_state)

    teleportation(k_party_obj)