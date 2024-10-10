from qiskit.quantum_info.operators import Operator
from entanglement_measures import entanglement_measures

class locc_controller:
    '''
    Args:

    protocol: An array of locc_operation objects

    k_party_obj: an object of class k_party

    '''

    def __init__(self, protocol, k_party_obj, execution_type):
        self.protocol = protocol
        self.k_party_obj = k_party_obj
        self.execution_type = execution_type
        self.ee_strings = []

    def execute_protocol(self):
        if not self.protocol or not self.k_party_obj:
            raise ValueError("LOCC Operation or K Party instance not created.")

        # Get the number of parties in the k_party_obj (assuming it has an attribute `parties`)
        all_party_indices = set(range(self.k_party_obj.parties))  # Create a set of all party indices


        for locc_op in self.protocol:
            qudit_index = self.k_party_obj.get_qudit_index_in_state(locc_op.party_index, locc_op.qudit_index)

            if locc_op.operation_type == "default":
                self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "conditional_operation":
                #retrieve the measurement result and evaluate the 
                print("Stored Measurement outcome for ", locc_op.condition[0], locc_op.condition[1], " = ", self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])))
                if self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])) == locc_op.condition[2]:
                    print("Applying operator = ", locc_op.operator)
                    self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "measure":
                outcome, self.k_party_obj.q_state = self.k_party_obj.q_state.measure([qudit_index])
                self.k_party_obj.measurement_result[(locc_op.party_index, qudit_index)] = outcome

                # Set PartyA as the party involved in the current LOCC operation
                partyA_indices = [locc_op.party_index]  # Wrap in a list to pass to the entanglement measures method

                # Set PartyB as every other party (all parties except PartyA)
                partyB_indices = list(all_party_indices - set(partyA_indices))  # Exclude PartyA from the set

                # Instantiate the entanglement_measures class (assuming it requires a state and parties as input)
                entanglement_calculator = entanglement_measures(self.k_party_obj.q_state, partyA_indices, partyB_indices)

                #save the measurement outcome which will be used in the next conditional operation
                self.k_party_obj.measurement_result[(locc_op.party_index, qudit_index)] = outcome

            if self.execution_type == "upper bound":
                    entanglement_entropy = entanglement_calculator.get_le_upper_bound()
            elif self.execution_type == "lower bound":
                entanglement_entropy = entanglement_calculator.get_le_lower_bound()

            self.ee_strings.append(f"Entanglement entropy between Party {partyA_indices[0]} and the rest: {entanglement_entropy}")
        
        output_file = "measurement_scene.mp4"

        return output_file, self.k_party_obj, self.ee_strings
    

    '''
    Executes the protocol by checking the type of each locc_operation and applying it one by one in a loop
    (Might be possible to parallelise the loop in the future)
    '''
    def execute_protocol_old(self):
        for locc_op in self.protocol:
            #get the qudit index within the statevector
            qudit_index = self.k_party_obj.get_qudit_index_in_state(locc_op.party_index, locc_op.qudit_index)

            #just apply the local operator
            if locc_op.operation_type == "default":
                self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "conditional_operation":
                #retrieve the measurement result and evaluate the 
                print("Stored Measurement outcome for ", locc_op.condition[0], locc_op.condition[1], " = ", self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])))
                if self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])) == locc_op.condition[2]:
                    print("Applying operator = ", locc_op.operator)
                    self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "measure":
                #perform measurement
                outcome, self.k_party_obj.q_state = self.k_party_obj.q_state.measure([qudit_index])
                print("Outcome is ", outcome)

                #save the measurement outcome which will be used in the next conditional operation
                self.k_party_obj.measurement_result[(locc_op.party_index, qudit_index)] = outcome

        print("After protocol run")
        print(self.k_party_obj.q_state)
        # return self.k_party_obj