from k_party import KParty
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from qiskit.quantum_info import Statevector
from quantum_state_controller import quantum_state_controller

class k_party_controller():
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.k_party_obj = None
        self.num_parties_field = None
        self.party_dim = None
        self.party_to_index = {}
        self.party_names = None

    def handle_create_k_party(self, party_names, k_entry, quantum_state_entry, num_qudits_entries, party_dim_entries):
        try:
            if party_names == "":
                raise ValueError("Please enter 'Party Names' field")
            
            self.party_names = party_names.split(',')

            k = int(k_entry)
            state_desc = []  # Description of the multi-party system
            dims = [] # overall dimension of k party
            
            for i in range(k):
                num_qudits_str = num_qudits_entries[i].text().strip()
                party_dim_str = party_dim_entries[i].text().strip()

                if num_qudits_str == '' or party_dim_str == '':
                    raise ValueError("Please enter values for all fields.")

                num_qudits = int(num_qudits_str)
                party_dim = int(party_dim_str)

                # Append to state_desc as (number of qudits, dimensions of each qudit)
                state_desc.append((num_qudits, [party_dim] * num_qudits))

                dims.append(party_dim)
            # Create the quantum state using QuantumStateController
            q_controller = quantum_state_controller(quantum_state_entry, num_qudits, state_desc)
            q_state = q_controller.create_quantum_state()  # Get the quantum state (superposition or ground)

            # Create the KParty object with the generated state
            self.k_party_obj = KParty(k, dims, state_desc, q_state, self.party_names)
            
            QMessageBox.information(self.parent_window, "KParty Created", f"KParty instance created with {k} parties.")

            return self.k_party_obj

        except ValueError as e:
            QMessageBox.critical(self.parent_window, "Input Error", str(e))

    def create_initial_state(self, dims): # double check if this is correct
        return Statevector.from_label('0' * dims)
    
    def parse_dimension_input(self, dimension_input):
        """
        Parses the input from the dimension entry and converts it to a list of integers.

        Args:
            dimension_input (str): The input string from the QLineEdit widget.

        Returns:
            list: A list of integers representing the dimensions of each qudit.

        Raises:
            ValueError: If the input is not valid.
        """
        if dimension_input.strip() == "":
            raise ValueError("Input cannot be empty.")

        try:
            # Split the input string by commas and strip whitespace
            dimensions = [dim.strip() for dim in dimension_input.split(",")]
            # Convert to integers
            int_dimensions = [int(dim) for dim in dimensions]
            return int_dimensions

        except ValueError as e:
            raise ValueError(f"Invalid input. Please enter integers separated by commas. Error: {str(e)}")
