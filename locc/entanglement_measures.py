#We might probably merge this class with the measures.py class that qiskit already has
import numpy as np
import math
from qiskit.quantum_info import shannon_entropy
from scipy import optimize

from scipy.linalg import expm
from k_party import k_party

from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import Statevector

import copy
from scipy.linalg import dft


class EntanglementMeasures:
    def __init__(self, N, psi, party_to_measure):
        self.k_party_obj = None
        self.N = N
        self.psi = psi
        self.party_to_measure = party_to_measure
        self.starting_parameters = []

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

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        res = optimize.minimize(self.minimise_le, v, method='nelder-mead',
                        options={'xatol': 1e-8, 'disp': True})
        print("Entanglement entropy = ", res.fun)
        return res.fun

    #upper bound for localisable entanglement
    def get_le_upper_bound(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj

        self.psi = self.k_party_obj.q_state
        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
            self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
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

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
                self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        self.starting_parameters = v

        for k_party_obj in arr:
            self.k_party_obj = k_party_obj

            self.psi = self.k_party_obj.q_state
            
            #start the optimisation using the final optimised parameters of the last state
            res = optimize.minimize(self.maximise_le, self.starting_parameters, method='nelder-mead',
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

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
                self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)
        self.starting_parameters = v

        for k_party_obj in arr:
            self.k_party_obj = k_party_obj

            self.psi = self.k_party_obj.q_state
            
            #start the optimisation using the final optimised parameters of the last state
            res = optimize.minimize(self.minimise_le, self.starting_parameters, method='nelder-mead',
                            options={'xatol': 1e-8, 'disp': True})
            print("Entanglement entropy = ", -1 * res.fun)
            max_le_array.append(-1 * res.fun)
        
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

    def get_le_multiple(self, k_party_obj, partyA, partyB):
        self.k_party_obj = k_party_obj

        #how many parameters are needed?
        #lets just measure with the same unitary for now
        v = np.random.uniform(0, 2*np.pi, self.k_party_obj.dims ** 2)

        if ((partyA == 0 and partyB == 1) or (partyA == 1 and partyB == 0)):
                self.party_to_measure = 2

        if ((partyA == 0 and partyB == 2) or (partyA == 2 and partyB == 0)):
            self.party_to_measure = 1

        if ((partyA == 1 and partyB == 2) or (partyA == 2 and partyB == 1)) :
            self.party_to_measure = 0

        self.party_to_measure = 3
        avg_entropy = self.maximise_le_multiparty(v) 

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
        U = np.sqrt(1/2) * dft(2)

        U_operator = Operator(U)

        #get the indices of the qudits we want to measure
        qudit_indices = self.k_party_obj.get_qudit_index_range(self.party_to_measure)

        all_posteriors = []
        all_posteriors.append((self.psi, 0))
        self.party_to_measure = self.k_party_obj.k - 1
        parties_measured = 0
        
        measurements_to_make_for_this_party = 1

        states_queue = []
        states_queue.append((self.psi, 0))

        while states_queue:
            print("Queue length = ", len(states_queue))

            if not isinstance(states_queue[0][0], Statevector):
                self.psi = Statevector(states_queue.pop(0)[0])

            else:
                self.psi = states_queue.pop(0)[0]
                
            print("Queue length after pop = ", len(states_queue))

            print("Psi = ", self.psi)
            print("Self.party to measure = ", self.party_to_measure)
            self.psi = self.psi.evolve(U_operator, [self.party_to_measure])
            q = k_party(self.k_party_obj.k, self.N, None, self.psi)

            all_posteriors = q.measure_all_possible_posteriors_qiskit(self.party_to_measure)

            for a in all_posteriors:
                states_queue.append(a)

            print("Queue length after APPEND = ", len(states_queue))

            #how to know that all measurements for this party has been done
            #there is an equation for that

            measurements_to_make_for_this_party -= 1
            if measurements_to_make_for_this_party == 0:
                print("Finished measurements for party_num = ", self.party_to_measure)
                parties_measured += 1
                self.party_to_measure -= 1

                if self.party_to_measure == 1:
                    measurements_to_make_for_this_party = 0
                    break

                else:
                    measurements_to_make_for_this_party = self.k_party_obj.dims ** (parties_measured)
                    print("Measurements to make for the next party = ", measurements_to_make_for_this_party)
                    
        print("QUEUE NOW =", len(states_queue))

        entropies = []
        probabilities = []
        posteriors = []

        print("Everything ok ")
    
        for state in states_queue:
            # if (self.party_to_measure == (self.k_party_obj.k - 1)):
            #     entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N ** 2, self.N)))
            #     posteriors.append(state[0].reshape(self.N ** 2, self.N))

            # else:
            #     entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N , self.N ** 2)))
            #     posteriors.append(state[0].reshape(self.N , self.N ** 2))
                
            #if (self.party_to_measure == (self.k_party_obj.k - 1)):
            #reshape 8,2 for 4-partite. But why?
            #Between which two parties are we computing the entanglement entropy
            #reshaping is 16,2 for 5-partite. But why?
            #I have to really understand the reshaping
            entropies.append(q.entanglement_entropy_for_state(state[0].reshape(16, 2)))
            posteriors.append(state[0].reshape(16, 2))

            # else:
            #     entropies.append(q.entanglement_entropy_for_state(state[0].reshape(self.N , self.N ** 2)))
            #     posteriors.append(state[0].reshape(self.N , self.N ** 2))
            probabilities.append(state[1])

        #compute weighted average
        print("Probabilites = ", probabilities)
        print("Entropies = ", entropies)
        avg_entropy = np.dot(probabilities, entropies)
        print("Avg entropy = ", avg_entropy)
        return -1 * avg_entropy


'''
We first measure the fifth party
Measuring that gives us a state
Then we measure the fourth party
But remember measurements have multiple possible outcomes

So when we measure the fifth party, we get get multiple outcomes and multiple states corresponding to those outcomes
We have to store all those states
And then measure the fourth party for all those outcomes

So how many states do we have to measure
1 + (num of parties - 3) * qudit_dimension

In case of qubits
For 3: 1 
For 4: 1 + 1*2. How? Once we have measured the fifth party. we have two states. we have to measure both these states
For 5: 1 + 2*2

Total measurement outcomes = (1 + (num of parties - 3) * qudit_dimension) * qudit_dimension

So how should we setup the loop?
Loop over parties?
Otherwise just loop until number_of_parties_parties == (k - 2)
Okay

Yes this is the stop point

Once we are inside the loop, what do we do?
Call the measure function on the state
What will it give in return?
It will give us outcomes, states

Now we this our new state
Do the outcomes matter?
So for each state, we store the state itself and its outcome probability
Then in the end we are left 
Yes they should. They are the probability. You cannot ignore those


In the end when we compute entanglement entropy , when we are left with the final bipartite state

The outcomes do matter. Because the posterior state depends on that outcome
So when we have the posterior state, it will 

In the end, we will have many bipartite states

And the probability outcome their would matter

Is this how localizable entanglement is defined?
Yes

But here is the question?
How many bipartite states do we end up with?
Lets start with 4 partite state
We measure this state and get 2 tripartite states
Yes each state corresponding to an outcome
Now we measure the 2 tripartite states
How many bipartite states do we get?
For each tripartite state, we get 2 bipartite states

So finally for a 4-partite state we get in the end, 2 ^ 2 = 4. bipartite state

(qudit_dimension)^ k - 2 bipartite states
For 5 partite state, we should then get 2 * 3 = 6 bipartite states
How many do we get?

2^(3) = 8
We start with a 5 partite state
And get 2, 4-partite states

So we should have actually had 8 bipartite states in the end

Yes, that is the right equation
Ok so for a 4-partite state, we get 4 bipartite states
What do we do with them?

We measure the entanglement entropies for each of those 4 bipartite states
Are those 4 bipartite states equally likely
Absolutely not

So for all those 4 bipartite states, we need the probabilities of those states occuring

We are performing local measurements

For an optimiser, can we give all these variables at once?
The other way would be to optimise for 1 party and then random unitaries for the others
But then it is a question of how many random unitaries

For now, we can have all the parameters in the function. And then we optimize for that.
Yes

But wait, the unitaries for each measurement
What to do about that?

Do we evolve with the same unitary for all the measurements?
No. But we have that many parameters ready

OK
How many parameters will be needed for 4-partite state of qubits?


2^(2) bipartite states in the end
Its not about that. Its about how many single qubit local measurements we have to make
Yes

1 + (num of parties - 3) * qudit_dimension measurements

For each measurement we need measurements^2 parameters
So for 4-partite qubit state, we need

1 + (num of parties - 3) * qudit_dimension
= 1 + (4-3) * 2
= 1 + 2
= 3

3^4 = 27 parameters

For a 5-partite state we would need 5 ^4 = 625 parameters
We could try, and then think about the way of doing it one by one.
Yes

How is it done one by one
Optimise for one measurement and then apply random unitaries 
In the end now we have one unitary fixed. 
Then optimise for another unitary with the fixed one fixed and random unitaries on the remaining one
But now the problem is this, applying the same random unitary to the other parties, or a different one in each run
Probably a different run in each one

There is no guarantee that the basis which yielded optimal for this random unitary
The random unitary has to be the same across the optimisation
If its different, then there is no comparison basis for the optimal basis
Yes, so we try this after the all parameters are once

This looks like a greedy algorithm

Can we solve it using divide and conquer?
How is divide and conquer even applicable here?
If these are local measurements, why cant we do them separately?

If we do one by one, how is that even going to work.


After this we should definitely find the optimal way of measuring LE from the paper


So we pass all the parameters.
That problem is solved
'''
