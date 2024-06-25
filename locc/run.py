import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from qiskit.quantum_info import Statevector, shannon_entropy
from qiskit.circuit.library import XGate, HGate, CXGate

'''
Tkinter GUI that will allow user to create a locc operation (protocol) object and a k party object.
Once objects are created will allow user to execute protocol.

'''

class locc_operation:
    '''
    Args:

    party_index: index of the party on which this operation is to be applied

    qudit_index: index of the qudit on which the operation is to be applied

    operation_type: Possible values are "measurement", "conditional_operation", "default"

    condition: A tuple of (party_index, qudit_index, measurement_result})

    operator: Qiskit gate or any unitary operation to be applied

    Example:
    locc_op4.party_index = 1
    locc_op4.qudit_index = 0
    locc_op4.operation_type = "conditional_operation"
    locc_op4.condition = (0, 0, 1)
    locc_op4.operator = Gate.X

    The above example means that if the 0th qudit of the 0th party measures 1, then apply X gate to the 0th qudit of the first party
    '''

    def __init__(self, party_index, qudit_index, operation_type, operator=None, condition=None):
        self.party_index = party_index
        self.qudit_index = qudit_index
        self.operation_type = operation_type
        self.operator = operator
        self.condition = condition

class k_party:
    '''
    Args:
    k = the number of parties

    state_desc is an array of 2-tuples where first entry is no. of qudits each party has
    and second entry is the dimension of each qudit. Size of array state_desc = k
    
    Example:[(2, [3, 3]), (4, [2, 2, 2, 2]), (1, [2])]. Here party A has 2 qutrits, party B has 4 qubits, party C has 1 qubit

    measurement_result has a 2-tuple as key of the form (party_index, qudit_index) and the value is the measurement outcome
    '''

    def __init__(self, k, dims, state_desc, q_state, party_names=None):
        self.k = k
        self.dims = dims
        self.parties = k
        self.state_desc = state_desc
        self.q_state = q_state
        self.party_names = party_names
        self.measurement_result = {}

    def state_dim(self):
        state_dims = 1
        for s in self.state_desc:
            state_dims *= np.prod(s[1])
        return state_dims

    def get_dims_by_party(self, party_index):
        if party_index >= self.k:
            return "Party index out of bounds"
        return max(self.state_desc[party_index][1])

    def total_qudits(self):
        total_qudits = 0
        for s in self.state_desc:
            total_qudits += s[0]
        return total_qudits

    def get_qudit_index_in_state(self, party_index, qudit_index_within_party):
        qudits_before = 0
        for index, s in enumerate(self.state_desc):
            if index != party_index:
                qudits_before += s[0]
            else:
                break
        return qudits_before + qudit_index_within_party

    def get_qudit_index_range(self, party_index):
        qudits_before = 0
        for index, s in enumerate(self.state_desc):
            if index != party_index:
                qudits_before += s[0]
            else:
                break
        return list(range(qudits_before, qudits_before + self.state_desc[party_index][0]))

    def copy(self):
        return

    def add_new_party(self, new_party_desc):
        self.k += 1
        self.state_desc.append(new_party_desc)

    def get_density_matrix(self):
        return np.outer(self.q_state.data, self.q_state.data.conj())

    def get_statevector(self):
        return

    def get_reduced_density_matrix(self, party_index):
        return

    def is_transformable(self, other_k_party_state):
        return False

    def local_operation(self, party_index, qudit_indices, unitary_operator):
        return

    def measure_different_basis(self, party_index, qudit_indices, basis_matrix):
        self.q_state.evolve(basis_matrix)
        self.measure(party_index, qudit_indices)

    def slocc_equivalence(self, other_k_party_state):
        probability = 0.0
        return probability

    def lu_equivalence(self, other_k_party_state):
        return False

    def lc_equivalence(self, other_k_party_state):
        return False

    def measure_all_possibilities(self, qubit_to_measure=None):
        outcomes = []
        all_possible_posteriors = []

        while len(outcomes) < self.dims:
            outcome, state = self.q_state.measure([qubit_to_measure])
            if outcome not in outcomes:
                outcomes.append(outcome)
                prob = self.q_state.probabilities([qubit_to_measure])[int(outcome)]
                all_possible_posteriors.append((state.data, prob))

        return all_possible_posteriors

    def bipartite_entropy(self, A, B):
        q_state_tensor = self.q_state.data.reshape([self.dims] * self.k)
        q_state_tensor = np.transpose(q_state_tensor, tuple(A + B))
        q_state_tensor = np.reshape(q_state_tensor, (self.dims ** len(A), self.dims ** len(B)))
        return self.entanglement_entropy_for_state(q_state_tensor)

    def entanglement_entropy(self):
        return self.E.entropy_using_singular_values(self.q_state)

    def entanglement_entropy_for_state(self, state):
        u, singular_values, vT = np.linalg.svd(state)
        squared_singular_vals = np.square(singular_values)
        entanglement_entropy = shannon_entropy(squared_singular_vals, base=2)
        return entanglement_entropy

# Define k_party and locc_operation classes here (already provided in your code)

class locc_controller:
    '''
    Args:
    protocol: An array of locc_operation objects
    k_party_obj: an object of class k_party
    '''
    def __init__(self, protocol, k_party_obj):
        self.protocol = protocol
        self.k_party_obj = k_party_obj
        self.measurement_result = {}

    '''
    Executes the protocol by checking the type of each locc_operation and applying it one by one in a loop
    (Might be possible to parallelise the loop in the future)
    '''
    def execute_protocol(self):
        for locc_op in self.protocol:
            qudit_index = self.k_party_obj.get_qudit_index_in_state(locc_op.party_index, locc_op.qudit_index)

            if locc_op.operation_type == "default":
                self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "conditional_operation":
                stored_result = self.measurement_result.get((locc_op.condition[0], locc_op.condition[1]), None)
                
                if stored_result is not None and stored_result == locc_op.condition[2]:
                    self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

            elif locc_op.operation_type == "measure":
                outcome, self.k_party_obj.q_state = self.k_party_obj.q_state.measure([qudit_index])
                print(f"Measurement outcome for party {locc_op.party_index}, qudit {locc_op.qudit_index} is {outcome}")
                self.measurement_result[(locc_op.party_index, locc_op.qudit_index)] = outcome

        print("After protocol execution:")
        print(self.k_party_obj.q_state)


def create_initial_state(dims):
    return Statevector.from_label('0' * dims)

def create_locc_operation():
    try:
        party_index = int(party_index_entry.get())
        qudit_index = int(qudit_index_entry.get())
        operation_type = operation_type_combobox.get()
        
        operator = None
        condition = None
        
        if operation_type == "conditional_operation":
            condition_party_index = int(condition_party_index_entry.get())
            condition_qudit_index = int(condition_qudit_index_entry.get())
            condition_measurement_result = int(condition_measurement_result_entry.get())
            condition = (condition_party_index, condition_qudit_index, condition_measurement_result)
            
            operator_choice = operator_combobox.get()
            if operator_choice == "XGate":
                operator = XGate()
            elif operator_choice == "HGate":
                operator = HGate()
            elif operator_choice == "CXGate":
                operator = CXGate()
        
        elif operation_type == "default":
            operator_choice = operator_combobox.get()
            if operator_choice == "XGate":
                operator = XGate()
            elif operator_choice == "HGate":
                operator = HGate()
            elif operator_choice == "CXGate":
                operator = CXGate()

        locc_op = locc_operation(party_index, qudit_index, operation_type, operator, condition)
        
        messagebox.showinfo("LOCC Operation", f"LOCC Operation Created:\nParty Index: {locc_op.party_index}\nQudit Index: {locc_op.qudit_index}\nOperation Type: {locc_op.operation_type}\nCondition: {locc_op.condition}\nOperator: {locc_op.operator}")
        
        global locc_operation_instance
        locc_operation_instance = [locc_op]  # Store the created locc_operation instance globally

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values.")

def create_k_party():
    try:
        global num_qudits_entries, qudit_dims_entries
        
        k = int(k_entry.get())
        
        state_desc = []
        dims = 1
        
        for i in range(k):
            num_qudits_str = num_qudits_entries[i].get().strip()
            qudit_dims_str = qudit_dims_entries[i].get().strip()
            
            if num_qudits_str == '' or qudit_dims_str == '':
                raise ValueError("Please enter values for all fields.")
            
            num_qudits = int(num_qudits_str)
            qudit_dims = list(map(int, qudit_dims_str.split(',')))
            
            if any(dim == 0 for dim in qudit_dims):
                raise ValueError("Dimension values cannot be zero.")
            
            state_desc.append((num_qudits, qudit_dims))
            dims *= np.prod(qudit_dims)
        
        q_state = create_initial_state(dims)
        party_names = party_names_entry.get().split(',') if party_names_entry.get() else None
        
        global k_party_instance
        k_party_instance = k_party(k, dims, state_desc, q_state, party_names)
        messagebox.showinfo("k_party Created", f"k_party instance created with {k} parties.")
        
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


def execute_protocol():
    global k_party_instance, locc_operation_instance
    
    if k_party_instance is None:
        messagebox.showerror("Error", "k_party instance not created.")
        return
    
    if locc_operation_instance is None:
        messagebox.showerror("Error", "locc_operation instance not created.")
        return
    
    # Create locc_controller instance and execute protocol
    controller = locc_controller(locc_operation_instance, k_party_instance)
    controller.execute_protocol()


# Create the main window
root = tk.Tk()
root.title("Quantum Operations")

# LOCC Operation Creator
ttk.Label(root, text="Party Index:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
party_index_entry = ttk.Entry(root)
party_index_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="Qudit Index:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
qudit_index_entry = ttk.Entry(root)
qudit_index_entry.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Operation Type:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
operation_type_combobox = ttk.Combobox(root, values=["measurement", "conditional_operation", "default"])
operation_type_combobox.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Operator:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
operator_combobox = ttk.Combobox(root, values=["XGate", "HGate", "CXGate"])
operator_combobox.grid(row=3, column=1, padx=10, pady=5)

# Conditional Operation Specific Inputs
ttk.Label(root, text="Condition Party Index:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
condition_party_index_entry = ttk.Entry(root)
condition_party_index_entry.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(root, text="Condition Qudit Index:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
condition_qudit_index_entry = ttk.Entry(root)
condition_qudit_index_entry.grid(row=5, column=1, padx=10, pady=5)

ttk.Label(root, text="Condition Measurement Result:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
condition_measurement_result_entry = ttk.Entry(root)
condition_measurement_result_entry.grid(row=6, column=1, padx=10, pady=5)

ttk.Button(root, text="Create LOCC Operation", command=create_locc_operation).grid(row=7, column=0, columnspan=2, pady=10)

# k_party Creator
ttk.Label(root, text="Number of Parties (k):").grid(row=8, column=0, padx=10, pady=5, sticky="e")
k_entry = ttk.Entry(root)
k_entry.grid(row=8, column=1, padx=10, pady=5)

num_qudits_entries = []
qudit_dims_entries = []

party_frame = ttk.Frame(root)
party_frame.grid(row=9, column=0, columnspan=2, pady=10)

def add_party_entries():
    global num_qudits_entries, qudit_dims_entries
    
    for widget in party_frame.winfo_children():
        widget.destroy()
    
    num_qudits_entries = []
    qudit_dims_entries = []
    
    k = int(k_entry.get())
    for i in range(k):
        ttk.Label(party_frame, text=f"Number of Qudits for Party {i+1}:").grid(row=i*2, column=0, padx=10, pady=5, sticky="e")
        num_qudits_entry = ttk.Entry(party_frame)
        num_qudits_entry.grid(row=i*2, column=1, padx=10, pady=5)
        num_qudits_entries.append(num_qudits_entry)
        
        ttk.Label(party_frame, text=f"Dimensions of Each Qudit for Party {i+1} (comma-separated):").grid(row=i*2+1, column=0, padx=10, pady=5, sticky="e")
        qudit_dims_entry = ttk.Entry(party_frame)
        qudit_dims_entry.grid(row=i*2+1, column=1, padx=10, pady=5)
        qudit_dims_entries.append(qudit_dims_entry)

ttk.Button(root, text="Add Party Entries", command=add_party_entries).grid(row=10, column=0, columnspan=2, pady=10)

ttk.Label(root, text="Party Names (comma-separated, optional):").grid(row=11, column=0, padx=10, pady=5, sticky="e")
party_names_entry = ttk.Entry(root)
party_names_entry.grid(row=11, column=1, padx=10, pady=5)

ttk.Button(root, text="Create k_party", command=create_k_party).grid(row=12, column=0, columnspan=2, pady=10)

# Execute Protocol Button
ttk.Button(root, text="Execute Protocol", command=execute_protocol).grid(row=13, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
