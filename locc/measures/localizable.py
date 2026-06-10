#We might probably merge this class with the measures.py class that qiskit already has
import numpy as np
from qiskit.quantum_info import shannon_entropy, Operator, Statevector
from scipy import optimize
from scipy.linalg import expm
from k_party import k_party

class LocalizableEntanglement:
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
        
        #v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        v = np.random.uniform(0, 2*np.pi, (self.k_party_obj.k - 2) * self.k_party_obj.dims ** 2)


        if self.k_party_obj.k > 3:
            res = optimize.minimize(self.minimise_le_multiparty, v, method='nelder-mead',
                        options={'xatol': 1e-5, 'disp': True, 'maxiter':40, 'maxfev': 40})
            print("Entanglement entropy = ", res.fun)
            return res.fun

        else:

            res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                            options={'xatol': 1e-5, 'disp': True})
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

        # v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        v = np.random.uniform(0, 2*np.pi, (self.k_party_obj.k - 2) * self.k_party_obj.dims ** 2)

        if self.k_party_obj.k > 3:
            res = optimize.minimize(self.maximise_le_multiparty, v, method='nelder-mead',
                        options={'xatol': 1e-5, 'disp': True})
            print("Entanglement entropy = ", -1 * res.fun)
            return -1 * res.fun

        else:
            res = optimize.minimize(self.maximise_le, v, method='nelder-mead',
                            options={'xatol': 1e-5, 'disp': True})
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
                            options={'xatol': 1e-5, 'disp': True})
                print("Multiparty Entanglement entropy = ", -1 * res.fun)
                min_le_array.append(res.fun)


            else:
                res = optimize.minimize(self.maximise_le, v, method='nelder-mead',
                                options={'xatol': 1e-5, 'disp': True})
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

            if self.k_party_obj.k > 3:
                res = optimize.minimize(self.minimise_le_multiparty, v, method='nelder-mead',
                            options={'disp': True, 'maxiter':40, 'maxfev': 40})
                print("Entanglement entropy = ", res.fun)
                max_le_array.append(res.fun)


            else:
                res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                                options={'disp': True})
                print("Entanglement entropy = ",  res.fun)
                max_le_array.append(res.fun)
        
        return max_le_array

    
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
        return -1 * self.minimise_le_multiparty(v)

    def minimise_le_multiparty(self, v):
        self.psi = self.k_party_obj.q_state

        #qudits_to_measure = self.k_party_obj.state_desc[self.party_to_measure][0]
        qudits_to_measure = self.k_party_obj.k - 2

        #print("qudits to measure =", qudits_to_measure)
        opt_parameters_list = np.array_split(v, qudits_to_measure)

        # print("opt parameters list =", opt_parameters_list)
        # print("opt parameters list size =", len(opt_parameters_list))

        #which parties to measure in what order
        parties_to_measure = []
        for party_index in range(self.k_party_obj.k - 1, -1, -1):
            if party_index != self.partyA and  party_index != self.partyB:
                parties_to_measure.append(party_index)

        unitaries = {}
        #for every party's measurement, generate a different unitary
        for index, o in enumerate(opt_parameters_list):
            #generate unitary matrix
            M = np.zeros((self.N, self.N), dtype = complex)
            for i in range(0,  self.N):
                M[i][i] = o[i]
            
            vector_index = self.N
            for row in range(0,  self.N - 1):
                for column in range(row + 1,  self.N):
                    M[row][column] = o[vector_index] + 1j * o[vector_index+1]
                    M[column][row] = o[vector_index] - 1j * o[vector_index+1]
                    vector_index += 2

            U = expm(1j * M)
            unitaries[parties_to_measure[index]] = U


        #get the indices of the qudits we want to measure
        #qudit_indices = self.k_party_obj.get_qudit_index_range(self.party_to_measure)

            
        #print("Parties to measure = ", parties_to_measure)
        parties_measured = 0
        
        measurements_to_make_for_this_party = 1

        states_queue = []
        
        states_queue.append((self.psi, 1))
        self.party_to_measure = parties_to_measure[0]
        U_operator = unitaries[self.party_to_measure]

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


                if len(parties_to_measure) == 0:
                    measurements_to_make_for_this_party = 0
                    break

                else:
                    measurements_to_make_for_this_party = self.k_party_obj.dims ** (parties_measured)
                    #print("Parties to measure here= ", parties_to_measure)
                    self.party_to_measure = parties_to_measure[0]
                    U_operator = unitaries[self.party_to_measure]

                    #print("Measurements to make for the next party = ", measurements_to_make_for_this_party)
                    
        entropies = []
        probabilities = []
        posteriors = []
    
        for state in states_queue:
            dim1 = int(self.k_party_obj.dims ** (self.k_party_obj.k-1))
            dim2 = int(self.k_party_obj.dims ** (self.k_party_obj.k-2))
            dim3 = int(self.k_party_obj.state_dim() / dim2)
            if self.k_party_obj.k == 4:
                if (self.partyA == 3 and self.partyB == 2) or (self.partyA == 3 and self.partyB == 1) or (self.partyA == 2 and self.partyB == 3) or (self.partyA == 1 and self.partyB == 3):
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.k_party_obj.dims, dim1)))
                    
                elif (self.partyA == 1 and self.partyB == 2) or (self.partyA == 2 and self.partyB == 1):
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim2, dim3)))

                else:
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim1, self.k_party_obj.dims)))


            elif self.k_party_obj.k == 5:
                if (self.partyA == 3 and self.partyB == 2) or (self.partyA == 2 and self.partyB == 4) or (self.partyA == 3 and self.partyB == 4) :
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.k_party_obj.dims, dim1)))
                    
                elif (self.partyA == 1 and self.partyB == 2) or (self.partyA == 2 and self.partyB == 1):
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim2, dim3)))

                elif (self.partyA == 3 and self.partyB == 1) or (self.partyA == 4 and self.partyB == 1) or (self.partyA == 2 and self.partyB == 3):
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim3, dim2)))

                else:
                    entropies.append(q.entanglement_entropy_for_state(state[0].reshape(dim1, self.k_party_obj.dims)))

            posteriors.append(state[0].reshape(dim1, self.k_party_obj.dims))
            probabilities.append(state[1])

        #compute weighted average
        # print("Probabilites = ", probabilities)
        # print("Entropies = ", entropies)
        self.starting_parameters = v

        avg_entropy = np.dot(probabilities, entropies)
        return 1 * avg_entropy