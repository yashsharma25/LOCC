import numpy as np

# Take the partial trace
def partial_trace(dm):
    # partial trace the second space
    reduced_dm = np.einsum('jiki->jk', dm)
    print(reduced_dm)
    return reduced_dm

def majorisation(reduced_psi, reduced_phi):
    lambda_psi, vecs = np.linalg.eig(reduced_psi)
    lambda_phi, vecs = np.linalg.eig(reduced_phi)

    print("Eigenvalues")
    print(lambda_psi)
    print(lambda_phi)

    for j in range(len(lambda_psi)):
        if not sum(lambda_psi[0:j]) <= sum(lambda_phi[0:j]):
            return False

    #at every k, vector a's elements sum lesser than or equal to vector b's elements
    return True


def get_density_matrix(statevec):
    return np.outer(statevec, statevec.conj())