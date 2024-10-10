import re
import numpy as np
from qiskit.quantum_info import Statevector
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class quantum_state_controller():
    def __init__(self, quantum_state_entry, num_qudits, state_desc):
        self.quantum_state_entry = quantum_state_entry
        self.num_qudits = num_qudits
        self.state_desc = state_desc  # Description of k-party system

    def create_quantum_state(self):
        user_input = self.quantum_state_entry.strip()

        if user_input == "":
            # Create a ground state if the input is empty
            q_state = self.create_initial_statevector()
            print("Created ground state:", q_state)
        else:
            try:
                # Parse the user input for a superposition state
                superposition_terms = self.parse_state_input(user_input)
                q_state = self.create_superposition_vector(superposition_terms)
                print("Created superposition state:", q_state)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Invalid state input: {e}")
                return  # Exit the method if there was an error

        return q_state  # Return the created quantum state

    def create_initial_statevector(self):
        """
        Initialize a ground state for the entire k-party system.
        """
        total_dim = 1
        for party in self.state_desc:
            total_dim *= np.prod(party[1])  # Multiply dimensions for each party

        # Initialize statevector as |00...0>
        initial_state = np.zeros(total_dim, dtype=complex)
        initial_state[0] = 1.0  # Ground state

        # Create the Statevector object
        state = Statevector(initial_state)

        return state
    
    def parse_state_input(self, input_str):
        input_str = input_str.replace(' ', '')
        terms = input_str.split('+')

        parsed_state = None

        # Regex patterns for matching coefficients and basis states
        coeff_pattern = r"([\d\/\*\.\-]*)"  # Matches things like "1/sqrt(2)", "-0.5", etc.
        basis_state_pattern = r"\|([01]+)\>"  # Matches things like "|00000>"

        for term in terms:
            match = re.match(coeff_pattern + basis_state_pattern, term)

            if match:
                coeff_str, basis_state_str = match.groups()

                # Evaluate the coefficient
                coeff = eval(coeff_str) if coeff_str else 1.0
                
                # Create the statevector for the basis state
                state_vector = coeff * Statevector.from_label(basis_state_str)

                # Add it to the total statevector
                if parsed_state is None:
                    parsed_state = state_vector
                else:
                    parsed_state += state_vector

        return parsed_state

    def create_superposition_vector(self, superposition_terms):
        """
        Creates a quantum state vector from superposition terms.
        """
        total_dim = 1
        for party in self.state_desc:
            total_dim *= np.prod(party[1])  # Calculate the total dimension for all parties

        state_vector = np.zeros(total_dim, dtype=complex)

        for coefficient, basis_state in superposition_terms:
            # Convert basis state like |001> to an index
            index = sum([int(bit) * (2 ** (self.num_qudits - 1 - i)) for i, bit in enumerate(basis_state)])
            state_vector[index] += coefficient  # Add coefficient to the corresponding index

        norm = np.linalg.norm(state_vector)
        if norm != 0:
            state_vector /= norm  # Normalize to ensure total probability is 1

        return Statevector(state_vector)
