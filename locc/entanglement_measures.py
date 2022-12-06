#We might probably merge this class with the measures.py class that qiskit already has
import numpy as np
import math
from qiskit.quantum_info import shannon_entropy
from scipy import optimize

from scipy.linalg import expm
from k_party import k_party

from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import Statevector

import time

class MinimizeStopper(object):
    def __init__(self, max_sec=10):
        self.max_sec = max_sec
        self.start   = time.time()

    def __call__(self, xk):
        # callback to terminate if max_sec exceeded
        elapsed = time.time() - self.start
        if elapsed > self.max_sec:
            print("Terminating optimization: time limit reached")
            return True
        else:
            # you might want to report other stuff here
            print("Elapsed: %.3f sec" % elapsed)

class EntanglementMeasures:
    def __init__(self, N, psi, party_to_measure):
        self.k_party_obj = None
        self.N = N
        self.psi = psi
        self.party_to_measure = party_to_measure
        self.starting_parameters = []
        self.partyA = 0
        self.partyB = 0

    def entanglement_entropy(self, quantum_state):
        return

    def entanglement_length(self, quantum_state):
        return

    def entanglement_fluctuation(self, quantum_state):
        return

    #lower bound for localisable entanglement
    def get_le_lower_bound(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj
        self.psi = self.k_party_obj.q_state
        self.partyA = partyA
        self.partyB = partyB

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        minimize_stopper = MinimizeStopper()

        if self.k_party_obj.k > 3:
            res = optimize.minimize(self.minimise_le_multiparty, v, method='nelder-mead',
                        options={'xatol': 1e-8, 'disp': True, 'maxiter':50})
            print("Entanglement entropy = ", res.fun)
            return res.fun

        else:

            res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                            options={'xatol': 1e-8, 'disp': True})
            print("Entanglement entropy = ", res.fun)
            return res.fun

    #upper bound for localisable entanglement
    def get_le_upper_bound(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj
        self.partyA = partyA
        self.partyB = partyB

        self.psi = self.k_party_obj.q_state
        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)

        if self.k_party_obj.k > 3:
            res = optimize.minimize(self.maximise_le_multiparty, v, method='nelder-mead',
                        options={'xatol': 1e-8, 'disp': True})
            print("Entanglement entropy = ", -1 * res.fun)
            return -1 * res.fun

        else:
            res = optimize.minimize(self.maximise_le, v, method='nelder-mead',
                            options={'xatol': 1e-8, 'disp': True})
            print("Entanglement entropy = ", -1 * res.fun)
            return -1 * res.fun

    '''
    Input: An array of k_party objects.
    Output: An array of maximum localizable entanglement for each state in the input array

    Use final optimisation parameters of the previous state as the initial parameters for the next state

    The party on which measurement is performed should be same for all states
    '''
    def get_le_upper_bound_evolving(self, arr, partyA, partyB):
        min_le_array = []
        self.partyA = partyA
        self.partyB = partyB

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
                self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = arr[0].dims ** 2

        v = np.random.uniform(0, 2*np.pi, arr[0].dims ** 2)
        self.starting_parameters = v

        for k_party_obj in arr:
            self.k_party_obj = k_party_obj

            self.psi = self.k_party_obj.q_state

            if self.k_party_obj.k > 3:
                res = optimize.minimize(self.maximise_le_multiparty, v, method='nelder-mead',
                            options={'xatol': 1e-8, 'disp': True})
                print("Multiparty Entanglement entropy = ", -1 * res.fun)
                min_le_array.append(res.fun)


            else:
                res = optimize.minimize(self.maximise_le, v, method='nelder-mead',
                                options={'xatol': 1e-8, 'disp': True})
                print("Entanglement entropy = ", -1 * res.fun)
                min_le_array.append(res.fun)
        
        return min_le_array

    '''
    Input: An array of k_party objects
    Output: An array of minimum localizable entanglement for each state in the input array

    Use final optimisation parameters of the previous state as the initial parameters for the next state

    The party on which measurement is performed should be same for all states

    '''    
    def get_le_lower_bound_evolving(self, arr, partyA, partyB):
        max_le_array = []
        self.partyA = partyA
        self.partyB = partyB

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
                self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, arr[0].dims ** 2)
        self.starting_parameters = v

        for k_party_obj in arr:
            self.k_party_obj = k_party_obj

            self.psi = self.k_party_obj.q_state
            minimize_stopper = MinimizeStopper()

            if self.k_party_obj.k > 3:
                res = optimize.minimize(self.minimise_le_multiparty, v, method='nelder-mead',
                            options={'xatol': 1e-8, 'disp': True})
                print("Entanglement entropy = ", res.fun)
                max_le_array.append(res.fun)


            else:
                res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                                options={'xatol': 1e-8, 'disp': True})
                print("Entanglement entropy = ",  res.fun)
                max_le_array.append(res.fun)
        
        return max_le_array

    def entropy_using_singular_values(self, state):
        u, singular_values, vT = np.linalg.svd(state)

        squared_singular_vals = np.square(singular_values)

        #shannon_entropy accepts a probability vector as input
        #singular values sum up to 1 and all elements are >= 0 so it is a probability vector
        entanglement_entropy = shannon_entropy(squared_singular_vals, base=2)

        return entanglement_entropy

    def von_neuman_entropy(self, rho):
        eigen_values = np.linalg.eigvals(rho)

        # Drop zero eigenvalues so that log2 is defined
        my_list = [x for x in eigen_values.tolist() if x.real > 0]
        eigen_values = np.array(my_list)
        #print("Eigen values = ", eigen_values)

        entropy = 0

        for ev in eigen_values:
            #print("Eigen value = ", ev.real)
            #print("Entropy = ", ev.real * math.log2(ev.real))
            entropy += ev * math.log2(ev.real)

        entropy *= -1
        return entropy

    #by using the -tr(rho log rho)
    def von_neumann_entropy_using_trace(rho):
        R = rho * (np.linalg.logm(rho) / np.linalg.logm(np.matrix([[2]])))
        S = -np.matrix.trace(R)
        return S

    
    def minimise_le(self, v):
        self.psi = self.k_party_obj.q_state

        #generate unitary matrix
        M = np.zeros((self.N, self.N), dtype = complex)
        for i in range(0,  self.N):
            M[i][i] = v[i]
        
        vector_index = self.N
        for row in range(0,  self.N - 1):
            for column in range(row + 1,  self.N):
                M[row][column] = v[vector_index] + 1j * v[vector_index+1]
                M[column][row] = v[vector_index] - 1j * v[vector_index+1]
                vector_index += 2

        U = expm(1j * M)

        U_operator = Operator(U)
        self.psi = self.psi.evolve(U_operator, [self.party_to_measure])

        q = k_party(self.k_party_obj.k, self.k_party_obj.dims, self.k_party_obj.state_desc, self.psi)
        all_possible_posteriors = q.measure_all_possible_posteriors_qiskit(self.party_to_measure)
        
        entropies = []
        probabilities = []
        posteriors = []

        for state in all_possible_posteriors:
            if (self.party_to_measure == 2):
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N ** 2, self.N)))
                posteriors.append(state[0].reshape(self.N ** 2, self.N))

            else:
                entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N , self.N ** 2)))
                posteriors.append(state[0].reshape(self.N , self.N ** 2))
                
         
            probabilities.append(state[1])

        #compute weighted average
        avg_entropy = np.dot(probabilities, entropies)
        self.starting_parameters = v

        return avg_entropy


    def maximise_le(self, v):
        return -1 * self.minimise_le(v)

    def maximise_le_multiparty(self, v):
        self.psi = self.k_party_obj.q_state

        # qudits_to_measure = self.k_party_obj.state_desc[self.party_to_measure][0]

        # opt_parameters_list = np.array_split(v, qudits_to_measure)

        # unitaries = []
        # for o in opt_parameters_list:
        #     #generate unitary matrix
        #     M = np.zeros((self.N, self.N), dtype = complex)
        #     for i in range(0,  self.N):
        #         M[i][i] = o[i]
            
        #     vector_index = self.N
        #     for row in range(0,  self.N - 1):
        #         for column in range(row + 1,  self.N):
        #             M[row][column] = o[vector_index] + 1j * o[vector_index+1]
        #             M[column][row] = o[vector_index] - 1j * o[vector_index+1]
        #             vector_index += 2

        #     U = expm(1j * M)
        #     unitaries.append(U)


        #generate unitary matrix
        M = np.zeros((self.N, self.N), dtype = complex)
        for i in range(0,  self.N):
            M[i][i] = v[i]
        
        vector_index = self.N
        for row in range(0,  self.N - 1):
            for column in range(row + 1,  self.N):
                M[row][column] = v[vector_index] + 1j * v[vector_index+1]
                M[column][row] = v[vector_index] - 1j * v[vector_index+1]
                vector_index += 2

        U = expm(1j * M)

        U_operator = Operator(U)

        #get the indices of the qudits we want to measure
        #qudit_indices = self.k_party_obj.get_qudit_index_range(self.party_to_measure)


        #which parties to measure in what order
        parties_to_measure = []
        for party_index in range(self.k_party_obj.k, 0, -1):
            if party_index != self.partyA and  party_index != self.partyB:
                self.party_to_measure = party_index - 1
                parties_to_measure.append(party_index - 1)
            
        #print("Parties to measure = ", parties_to_measure)
        parties_measured = 0
        
        measurements_to_make_for_this_party = 1

        states_queue = []
        
        states_queue.append((self.psi, 1))

        while states_queue:
            if not isinstance(states_queue[0][0], Statevector):
                previous_state_tuple =states_queue.pop(0)
                self.psi = Statevector(previous_state_tuple[0])
                prev_prob = previous_state_tuple[1]

            else:
                previous_state_tuple = states_queue.pop(0)
                self.psi = previous_state_tuple[0]
                prev_prob = previous_state_tuple[1]

            self.psi = self.psi.evolve(U_operator, [self.party_to_measure])
            q = k_party(self.k_party_obj.k, self.N, None, self.psi)

            all_posteriors = q.measure_all_possible_posteriors_qiskit(self.party_to_measure)

            for a in all_posteriors:
                x = (a[0], a[1] * prev_prob)
                states_queue.append(x)

            measurements_to_make_for_this_party -= 1
            if measurements_to_make_for_this_party == 0:
                #print("Finished measurements for party_num = ", self.party_to_measure)
                parties_to_measure.pop(0)
                parties_measured += 1

                self.party_to_measure = parties_to_measure[0] - 1

                if self.party_to_measure == 1:
                    measurements_to_make_for_this_party = 0
                    break

                else:
                    measurements_to_make_for_this_party = self.k_party_obj.dims ** (parties_measured)
                    #print("Measurements to make for the next party = ", measurements_to_make_for_this_party)
                    
        entropies = []
        probabilities = []
        posteriors = []
    
        for state in states_queue:
            dim1 = int(self.k_party_obj.dims ** (self.k_party_obj.k-1))
            entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim1, self.k_party_obj.dims)))
            posteriors.append(state[0].reshape(dim1, self.k_party_obj.dims))
            probabilities.append(state[1])

        #compute weighted average
        # print("Probabilites = ", probabilities)
        # print("Entropies = ", entropies)
        avg_entropy = np.dot(probabilities, entropies)
        return -1 * avg_entropy

    def minimise_le_multiparty(self, v):
        self.psi = self.k_party_obj.q_state

        # qudits_to_measure = self.k_party_obj.state_desc[self.party_to_measure][0]

        # opt_parameters_list = np.array_split(v, qudits_to_measure)

        # unitaries = []
        # for o in opt_parameters_list:
        #     #generate unitary matrix
        #     M = np.zeros((self.N, self.N), dtype = complex)
        #     for i in range(0,  self.N):
        #         M[i][i] = o[i]
            
        #     vector_index = self.N
        #     for row in range(0,  self.N - 1):
        #         for column in range(row + 1,  self.N):
        #             M[row][column] = o[vector_index] + 1j * o[vector_index+1]
        #             M[column][row] = o[vector_index] - 1j * o[vector_index+1]
        #             vector_index += 2

        #     U = expm(1j * M)
        #     unitaries.append(U)


        #generate unitary matrix
        M = np.zeros((self.N, self.N), dtype = complex)
        for i in range(0,  self.N):
            M[i][i] = v[i]
        
        vector_index = self.N
        for row in range(0,  self.N - 1):
            for column in range(row + 1,  self.N):
                M[row][column] = v[vector_index] + 1j * v[vector_index+1]
                M[column][row] = v[vector_index] - 1j * v[vector_index+1]
                vector_index += 2

        U = expm(1j * M)

        U_operator = Operator(U)

        #get the indices of the qudits we want to measure
        #qudit_indices = self.k_party_obj.get_qudit_index_range(self.party_to_measure)


        #which parties to measure in what order
        parties_to_measure = []
        for party_index in range(self.k_party_obj.k, 0, -1):
            if party_index != self.partyA and  party_index != self.partyB:
                self.party_to_measure = party_index - 1
                parties_to_measure.append(party_index - 1)
            
        #print("Parties to measure = ", parties_to_measure)
        parties_measured = 0
        
        measurements_to_make_for_this_party = 1

        states_queue = []
        
        states_queue.append((self.psi, 1))

        while states_queue:
            if not isinstance(states_queue[0][0], Statevector):
                previous_state_tuple =states_queue.pop(0)
                self.psi = Statevector(previous_state_tuple[0])
                prev_prob = previous_state_tuple[1]

            else:
                previous_state_tuple = states_queue.pop(0)
                self.psi = previous_state_tuple[0]
                prev_prob = previous_state_tuple[1]

            self.psi = self.psi.evolve(U_operator, [self.party_to_measure])
            q = k_party(self.k_party_obj.k, self.N, None, self.psi)

            all_posteriors = q.measure_all_possible_posteriors_qiskit(self.party_to_measure)

            for a in all_posteriors:
                x = (a[0], a[1] * prev_prob)
                states_queue.append(x)

            measurements_to_make_for_this_party -= 1
            if measurements_to_make_for_this_party == 0:
                #print("Finished measurements for party_num = ", self.party_to_measure)
                parties_to_measure.pop(0)
                parties_measured += 1

                self.party_to_measure = parties_to_measure[0] - 1

                if self.party_to_measure == 1:
                    measurements_to_make_for_this_party = 0
                    break

                else:
                    measurements_to_make_for_this_party = self.k_party_obj.dims ** (parties_measured)
                    #print("Measurements to make for the next party = ", measurements_to_make_for_this_party)
                    
        entropies = []
        probabilities = []
        posteriors = []
    
        for state in states_queue:
            dim1 = int(self.k_party_obj.dims ** (self.k_party_obj.k-1))
            entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim1, self.k_party_obj.dims)))
            posteriors.append(state[0].reshape(dim1, self.k_party_obj.dims))
            probabilities.append(state[1])

        #compute weighted average
        # print("Probabilites = ", probabilities)
        # print("Entropies = ", entropies)
        avg_entropy = np.dot(probabilities, entropies)
        return avg_entropy