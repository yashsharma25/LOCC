import numpy as np

class utils:
    # Take the partial trace
    def partial_trace(self, dm):
        # partial trace the second space
        reduced_dm = np.einsum('jiki->jk', dm)
        print(reduced_dm)
        return reduced_dm

    #return the schmidt coefficients
    def schmidt_coeff(self, quantum_state):
        return

    def schmidt_rank(self, quantum_state):
        rank = 1
        return rank

    def get_density_matrix(self, statevec):
        return np.outer(statevec, statevec.conj())

    def majorisation(self, reduced_psi, reduced_phi):
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