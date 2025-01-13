from qiskit.quantum_info.operators import Operator

class locc_controller:
    '''
    Args:

    protocol: An array of locc_operation objects

    k_party_obj: an object of class k_party

    '''

    def __init__(self, protocol, k_party_obj):
        self.protocol = protocol
        self.k_party_obj = k_party_obj

    '''
    Executes the protocol by checking the type of each locc_operation and applying it one by one in a loop
    (Might be possible to parallelise the loop in the future)
    '''
    def execute_protocol(self):
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
                # return [f"Outcome is: {outcome}.", self.k_party_obj] # returning a list where res[0] = a string describing outcome, and res[1] = k_party_obj itself