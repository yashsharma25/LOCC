from k_party import KParty
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from qiskit.quantum_info import Statevector

class KPartyController():
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.k_party = None
        self.num_parties_field = None
        self.party_dim = None
        self.party_to_index = {}
        self.party_names = None

    def handle_create_k_party(self, party_names, k_entry, dim_entry, num_qudits_entries):
        try:
            if party_names == "":
                raise ValueError("Please enter 'Party Names' field")
            
            print(party_names)
            
            k = int(k_entry)
            dims = int(dim_entry)
            
            state_desc = []
            
            for i in range(k):
                num_qudits_str = num_qudits_entries[i].text().strip()
                
                if num_qudits_str == '':
                    raise ValueError("Please enter values for all fields.")
                
                num_qudits = int(num_qudits_str)
                
                state_desc.append((num_qudits, [2]*num_qudits))
            
            q_state = self.create_initial_state(dims)
            self.party_names = party_names.split(',') if party_names else None
            
            self.party_to_index = {} # key: "party name", value: party index
            for i in range(len(self.party_names)):
                self.party_to_index[self.party_names[i]] = i

            self.k_party_obj = KParty(k, dims, state_desc, q_state, self.party_names)
            QMessageBox.information(self.parent_window, "k_party Created", f"k_party instance created with {k} parties.")
            
        except ValueError as e:
            QMessageBox.critical(self.parent_window, "Input Error", e)
            # QMessageBox.critical(self, "Input Error", "Please ensure all entries are integer values.")

    def create_initial_state(self, dims): # double check if this is correct
        return Statevector.from_label('0' * dims)