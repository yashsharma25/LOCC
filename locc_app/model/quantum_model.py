import numpy as np
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import XGate, HGate, CXGate
from model.k_party import k_party
from model.locc_operation import locc_operation
from sympy.physics.quantum.gate import H, X, Z #, CX

class QuantumModel:
    def __init__(self):
        self.quantum_state = None
        self.state_desc = []
        self.k = None
        self.k_party = None
        self.execution_type = None
        self.locc_protocol_obj = []

    def get_input_for_video(self):
        if not self.locc_protocol_obj or not self.k_party:
                raise ValueError("LOCC Operation or K Party instance not created.")
            
        return (self.locc_protocol_obj, self.k_party, self.execution_type)

    def save_execution_type(self, execution_type):
        self.execution_type = execution_type

    def save_locc_operation(self, party_index, qudit_index, operation_type, operator_choice, condition):
        print(operation_type)
        locc_op_str = ""
        print(operation_type)
        if operator_choice == "XGate":
            # operator = XGate()
            operator = np.array(X().get_target_matrix())
        elif operator_choice == "HGate":
            # operator = HGate()
            operator = np.array(H().get_target_matrix()).astype(np.float64)
        # elif operator_choice == "CXGate": # TO DO FIX CX IMPORT ERROR
            # operator = CXGate()
            # operator = np.array(CX().get_target_matrix()) # DOUBLE CHECK IF THIS WORKS
        elif operator_choice == "ZGate": # ADD THIS BUTTON TO THE UI
            operator = np.array(Z().get_target_matrix())
        elif operator_choice == "-" and operation_type == "measure":
            operator = None
        
        if condition == "-" and operation_type != "conditional_operation":
            condition = None
        elif operation_type == "conditional_operation":
            pass # condition = condition

        print(f"OPERATOR CHOICE: {operator_choice} AND OPERATOR: {operator}")
        locc_op = locc_operation(party_index, qudit_index, operation_type, operator, condition)

        self.locc_protocol_obj.append(locc_op)
        locc_op_str += f"LOCC Operation Created:\nParty Index: {locc_op.party_index}\nQudit Index: {locc_op.qudit_index}\n Operation Type: {locc_op.operation_type}\nCondition: {locc_op.condition}\nOperator: {locc_op.operator}\n\n"

        if self.locc_protocol_obj is None:
            raise ValueError("Error. LOCC Protocol has no items.")
        else:
            return f"LOCC Protocl created successfully, number of items in protocol: {len(self.locc_protocol_obj)} \n {locc_op_str}"

    def create_quantum_state(self, *args):
        print(args)
        amplitude_list, basis_state_list = args
        """
        Initialize the quantum state with a given state.
        """
        print(amplitude_list)
        print(basis_state_list)
        try:
            num_qubits = len(basis_state_list[0])
            state_vector = np.zeros(2**num_qubits, dtype=complex)

            for amp, basis in zip(amplitude_list, basis_state_list):
                index = int(basis, 2)
                state_vector[index] = amp

            self.quantum_state = Statevector(state_vector)

            bra_ket_notation = " + ".join(
                f"({amp})|{basis}⟩" for amp, basis in zip(amplitude_list, basis_state_list)
            )

            print(f"Quantum State:\n {bra_ket_notation}")

            return "Success. Quantum state created successfully."

        except Exception as e:
            return f"Error {str(e)}"
     
    def generate_state_desc_label_and_k_party(self, num_parties_input, num_qudits_input, dim_input):
        try:
            self.k = int(num_parties_input.text())
            self.dims = [] # every item in dims will be the same, keeping dims in list form to be consistent with exisitng k party class structure
            
            num_qudits_list = list(map(int, num_qudits_input.text().split(',')))
            if len(num_qudits_list) != self.k:
                raise ValueError(f"Number of parties ({self.k}) does not match the number of provided qudits ({len(num_qudits_list)}).")
            
            dim = int(dim_input.text())
            if dim <= 0:
                raise ValueError("The dimension of each qudit must be a positive integer.")

            for i in range(self.k):
                num_qudits_str = num_qudits_list[i]

                if num_qudits_str == '' or dim == '':
                    raise ValueError("Please enter values for all fields.")
                
                num_qudits = int(num_qudits_str)

                # Append to state_desc as (number of qudits, dimensions of each qudit)
                self.state_desc.append((num_qudits, [dim] * num_qudits))

                self.dims.append(dim)

            if self.quantum_state is None:
                raise ValueError("No quantum state created. Please create a state first.")
            
            self.k_party = k_party(
                k=self.k,
                dims=self.dims,
                state_desc=self.state_desc,
                q_state=self.quantum_state
            )

            return f"k_party_obj created. state_desc: {self.state_desc}, {self.k_party}"
        except Exception as e:
            return f"Error {str(e)}"
