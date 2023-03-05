from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures
from k_party import k_party

def GHZ(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))


    # ghz = ghz.tensor(Statevector.from_label('0'))
    # print(ghz)
    return ghz
    #print("Norm of state =", norm(psi.flatten()))

def GHZ_4(dims):
    psi = np.zeros((dims, dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims, dims))
    #print(ghz)
    return ghz

def GHZ_5(dims):
    psi = np.zeros((dims, dims, dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims, dims, dims))
    #print(ghz)
    return ghz

def GHZ_tensored_another(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))
    
    ghz_tensored_another = ghz.tensor(Statevector.from_label('0'))
    print(ghz_tensored_another)
    return ghz_tensored_another


# 1/sqrt(2) |00000> + |11110>
def GHZ_3_tensored_another(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))
    ghz_tensored_another = ghz.tensor(Statevector.from_label('00'))

    #print(ghz)
    return ghz_tensored_another

# em = EntanglementMeasures(3, GHZ(3), 3)

# k_party_obj1 = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))
# k_party_obj2 = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))

# em.get_le_upper_bound_evolving([k_party_obj1, k_party_obj2], 0, 1)

#now we compute the nursing numbers for this state
# k_party_obj = k_party(2, 2, [(1, [2]), (1, [2]), (1, [2])], GHZ(2))

# em = EntanglementMeasures(2, GHZ(2), 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)

# k_party_obj = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))

# em = EntanglementMeasures(3, GHZ(3), 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)
# em.get_le_upper_bound(k_party_obj, 1, 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)


# em.get_le_lower_bound(k_party_obj, 0, 2)
# em.get_le_lower_bound(k_party_obj, 0, 1)
# em.get_le_lower_bound(k_party_obj, 1, 2)

# em.get_le_lower_bound(k_party_obj, 0, 2)

# em = EntanglementMeasures(2, GHZ_tensored_another(2), 2)
# k_party_obj = k_party(2, 3, [(1, [2]), (1, [2]), (2, [2, 2])], GHZ_tensored_another(2))

# em.get_le_multiple(k_party_obj, 0, 1)


em = EntanglementMeasures(2, GHZ_5(2), 4)
k_party_obj = k_party(5, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2])], GHZ_5(2))

def bipartite_entropy_check():
    q_state_np = k_party_obj.q_state.data.reshape(2,2,2,2,2)
    print("Shape before = ", q_state_np.shape)
    reshape_tuple = (1,4,0,2,3)
    q_state_np = np.transpose(q_state_np, reshape_tuple)
    q_state_np = np.reshape(q_state_np, (4,8))

    print(q_state_np.shape)


# em = EntanglementMeasures(2, GHZ_4(2), 3)
# k_party_obj = k_party(4, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2])], GHZ_4(2))

# em.get_le_upper_bound(k_party_obj, 0, 1)


# for i in range(0, 4):
#     for j in range(i+1, 4):
#         print("i = ", i)
#         print("j = ", j)
#         # em.get_le_upper_bound(k_party_obj, i, j)
#         # em.get_le_lower_bound(k_party_obj, i, j)
#         A = set([i,j])
#         B = set(np.arange(4))

#         # Get new set with elements that are only in a but not in b
#         B = B.difference(A)
#         print("A = ", A, " B = ", B)
#         ee = k_party_obj.bipartite_entropy(list(A), list(B))
#         print('EE = ', ee)

for i in range(0, 5):
    for j in range(i+1, 5):
        print("i = ", i)
        print("j = ", j)
        # em.get_le_upper_bound(k_party_obj, i, j)
        # em.get_le_lower_bound(k_party_obj, i, j)
        A = set([i,j])
        B = set(np.arange(5))

        # Get new set with elements that are only in a but not in b
        B = B.difference(A)
        print("A = ", A, " B = ", B)
        ee = k_party_obj.bipartite_entropy(list(A), list(B))
        print('EE = ', ee)


#em.get_le_lower_bound(k_party_obj, 0, 1)