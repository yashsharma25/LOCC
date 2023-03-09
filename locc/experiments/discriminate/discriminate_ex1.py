from qiskit.quantum_info import Statevector
from locc_operation import locc_operation
from k_party import k_party
from locc_discriminate import locc_discriminate

import numpy as np

def discriminate(k_party_obj1, k_party_obj2):
    locc_op1 = locc_operation(0, 0, "measure")
    locc_op2 = locc_operation(1, 0, "measure")

    locc_discriminate_obj = locc_discriminate(k_party_obj1, k_party_obj2, [locc_op1, locc_op2])

    locc_discriminate_obj.discriminate()


if __name__ == "__main__":
    #this will be shared by both alice and Bob
    state1 = 1/np.sqrt(2)* (Statevector.from_label("00") + Statevector.from_label("11"))
    state2 = 1/np.sqrt(2)* (Statevector.from_label("01") + Statevector.from_label("10"))

    k_party_obj1 = k_party(2, 2, [(1, [2]), (1, [2])], state1)
    k_party_obj2 = k_party(2, 2, [(1, [2]), (1, [2])], state2)

    discriminate(k_party_obj1, k_party_obj2)

