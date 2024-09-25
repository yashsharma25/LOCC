import re
import numpy as np
from qiskit.quantum_info import Statevector
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class QuantumStateController():
    def __init__(self, quantum_state_entry, num_qudits, dims):
        self.quantum_state_entry = quantum_state_entry
        self.num_qudits = num_qudits
        self.dims = dims

    from PyQt5.QtWidgets import QLineEdit, QMessageBox

    def create_quantum_state(self):
        user_input = self.quantum_state_entry.strip()  # Get user input from QLineEdit

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
                # Handle any errors in parsing or state creation
                QMessageBox.critical(self, "Error", f"Invalid state input: {e}")
                return  # Exit the method if there was an error

        return q_state  # Return the created quantum state


    def create_initial_statevector(self):
        """
        Args:
            num_qudits: int, the number of qudits
            dimensions: list of ints, each element is the dimension of the respective qudit

        Returns:
            Statevector: the initialized quantum statevector (all qudits in their ground state)
        """
        
        # Validate input
        if len(self.dims) != self.num_qudits:
            raise ValueError("The number of qudits must match the length of the dimensions array.")
        
        # Create an initial ground state for each qudit
        total_dim = np.prod(self.dims)  # The total size of the Hilbert space
        initial_state = np.zeros(total_dim, dtype=complex)  # Initialize statevector as |000...0>
        initial_state[0] = 1.0  # Ground state: |00...0> -> This sets the first element to 1
        
        # Reshape to match the qudit dimensions
        state = Statevector(initial_state.reshape(self.dimensions))

        return state

    def parse_state_input(self, input_str):
        # remove white spaces and split the state string by '+'
        input_str = input_str.replace(' ', '')
        terms = input_str.split('+')

        parsed_state = None

        # Define regex patterns for matching coefficients and basis states
        coeff_pattern = r"([\d\/\*\.\-]*)"  # Matches things like "1/sqrt(2)", "-0.5", etc.
        basis_state_pattern = r"\|([01]+)\>"  # Matches things like "|00000>"

        for term in terms:
            match = re.match(coeff_pattern + basis_state_pattern, term)

            if match:
                coeff_str, basis_state_str = match.groups()

                # Evaluate the coefficient (e.g., 1/sqrt(2) -> 0.70710678118)
                coeff = eval(coeff_str) if coeff_str else 1.0
                
                # create the statevector for the given basis state
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

        Args:
            superposition_terms (list of tuples): Each tuple contains a coefficient
                                                and a list representing the basis state.
            num_qudits (int): The number of qudits in the quantum state.
            dim (int): The dimension of the quantum state vector (2^num_qudits).

        Returns:
            Statevector: The resulting quantum state vector.
        """
        # Initialize the state vector with zeros
        state_vector = np.zeros(self.dims, dtype=complex)

        for coefficient, basis_state in superposition_terms:
            # Convert basis state like |001> to an index
            index = sum([int(bit) * (2 ** (self.num_qudits - 1 - i)) for i, bit in enumerate(basis_state)])
            state_vector[index] += coefficient  # Add coefficient to the corresponding index

        # Normalize the state vector
        norm = np.linalg.norm(state_vector)
        if norm != 0:
            state_vector /= norm  # Normalize to ensure total probability is 1

        return Statevector(state_vector)


