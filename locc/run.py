import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QScrollArea)
import numpy as np
from qiskit.quantum_info import Statevector, shannon_entropy
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import locc_controller
from k_party import k_party
from locc_operation import locc_operation

class QuantumOperationsGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Operations")
        self.setGeometry(100, 100, 600, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # LOCC Operation Creator
        self.create_locc_operation_ui(scroll_layout)

        # k_party Creator
        self.create_k_party_ui(scroll_layout)

        # Execute Protocol Button
        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_protocol)
        scroll_layout.addWidget(execute_button)

        self.k_party_instance = None
        self.locc_operation_instance = None

    def create_locc_operation_ui(self, layout):
        layout.addWidget(QLabel("LOCC Operation Creator"))

        self.party_index_entry = QLineEdit()
        layout.addWidget(QLabel("Party Index:"))
        layout.addWidget(self.party_index_entry)

        self.qudit_index_entry = QLineEdit()
        layout.addWidget(QLabel("Qudit Index:"))
        layout.addWidget(self.qudit_index_entry)

        self.operation_type_combobox = QComboBox()
        self.operation_type_combobox.addItems(["measurement", "conditional_operation", "default"])
        layout.addWidget(QLabel("Operation Type:"))
        layout.addWidget(self.operation_type_combobox)

        self.operator_combobox = QComboBox()
        self.operator_combobox.addItems(["XGate", "HGate", "CXGate"])
        layout.addWidget(QLabel("Operator:"))
        layout.addWidget(self.operator_combobox)

        self.condition_party_index_entry = QLineEdit()
        layout.addWidget(QLabel("Condition Party Index (leave empty if N/A):"))
        layout.addWidget(self.condition_party_index_entry)

        self.condition_qudit_index_entry = QLineEdit()
        layout.addWidget(QLabel("Condition Qudit Index (leave empty if N/A):"))
        layout.addWidget(self.condition_qudit_index_entry)

        self.condition_measurement_result_entry = QLineEdit()
        layout.addWidget(QLabel("Condition Measurement Result (leave empty if N/A):"))
        layout.addWidget(self.condition_measurement_result_entry)

        create_locc_button = QPushButton("Create LOCC Operation")
        create_locc_button.clicked.connect(self.create_locc_operation)
        layout.addWidget(create_locc_button)

    def create_k_party_ui(self, layout):
        layout.addWidget(QLabel("k_party Creator"))

        self.k_entry = QLineEdit()
        layout.addWidget(QLabel("Number of Parties (k):"))
        layout.addWidget(self.k_entry)

        self.party_frame = QWidget()
        self.party_frame_layout = QVBoxLayout(self.party_frame)
        layout.addWidget(self.party_frame)

        add_party_button = QPushButton("Add Party Entries")
        add_party_button.clicked.connect(self.add_party_entries)
        layout.addWidget(add_party_button)

        self.party_names_entry = QLineEdit()
        layout.addWidget(QLabel("Party Names (comma-separated, optional):"))
        layout.addWidget(self.party_names_entry)

        create_k_party_button = QPushButton("Create k_party")
        create_k_party_button.clicked.connect(self.create_k_party)
        layout.addWidget(create_k_party_button)

    def create_locc_operation(self):
        try:
            party_index = int(self.party_index_entry.text())
            qudit_index = int(self.qudit_index_entry.text())
            operation_type = self.operation_type_combobox.currentText()
            
            operator = None
            condition = None
            
            if operation_type == "conditional_operation":
                condition_party_index = int(self.condition_party_index_entry.text())
                condition_qudit_index = int(self.condition_qudit_index_entry.text())
                condition_measurement_result = int(self.condition_measurement_result_entry.text())
                condition = (condition_party_index, condition_qudit_index, condition_measurement_result)
                
                operator_choice = self.operator_combobox.currentText()
                if operator_choice == "XGate":
                    operator = XGate()
                elif operator_choice == "HGate":
                    operator = HGate()
                elif operator_choice == "CXGate":
                    operator = CXGate()
            
            elif operation_type == "default":
                operator_choice = self.operator_combobox.currentText()
                if operator_choice == "XGate":
                    operator = XGate()
                elif operator_choice == "HGate":
                    operator = HGate()
                elif operator_choice == "CXGate":
                    operator = CXGate()

            locc_op = locc_operation(party_index, qudit_index, operation_type, operator, condition)
            
            QMessageBox.information(self, "LOCC Operation", f"LOCC Operation Created:\nParty Index: {locc_op.party_index}\nQudit Index: {locc_op.qudit_index}\nOperation Type: {locc_op.operation_type}\nCondition: {locc_op.condition}\nOperator: {locc_op.operator}")
            
            self.locc_operation_instance = [locc_op]

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid integer values.")

    def add_party_entries(self):
        for i in reversed(range(self.party_frame_layout.count())): 
            self.party_frame_layout.itemAt(i).widget().setParent(None)
        
        self.num_qudits_entries = []
        self.qudit_dims_entries = []
        
        k = int(self.k_entry.text())
        for i in range(k):
            self.party_frame_layout.addWidget(QLabel(f"Number of Qudits for Party {i+1}:"))
            num_qudits_entry = QLineEdit()
            self.party_frame_layout.addWidget(num_qudits_entry)
            self.num_qudits_entries.append(num_qudits_entry)
            
            self.party_frame_layout.addWidget(QLabel(f"Dimensions of Each Qudit for Party {i+1} (comma-separated):"))
            qudit_dims_entry = QLineEdit()
            self.party_frame_layout.addWidget(qudit_dims_entry)
            self.qudit_dims_entries.append(qudit_dims_entry)

    def create_k_party(self):
        try:
            k = int(self.k_entry.text())
            
            state_desc = []
            dims = 1
            
            for i in range(k):
                num_qudits_str = self.num_qudits_entries[i].text().strip()
                qudit_dims_str = self.qudit_dims_entries[i].text().strip()
                
                if num_qudits_str == '' or qudit_dims_str == '':
                    raise ValueError("Please enter values for all fields.")
                
                num_qudits = int(num_qudits_str)
                qudit_dims = list(map(int, qudit_dims_str.split(',')))
                
                if any(dim == 0 for dim in qudit_dims):
                    raise ValueError("Dimension values cannot be zero.")
                
                state_desc.append((num_qudits, qudit_dims))
                dims *= np.prod(qudit_dims)
            
            q_state = self.create_initial_state(dims)
            party_names = self.party_names_entry.text().split(',') if self.party_names_entry.text() else None
            
            self.k_party_instance = k_party(k, dims, state_desc, q_state, party_names)
            QMessageBox.information(self, "k_party Created", f"k_party instance created with {k} parties.")
            
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", str(e))

    def create_initial_state(self, dims):
        return Statevector.from_label('0' * dims)

    def execute_protocol(self):
        if self.k_party_instance is None:
            QMessageBox.critical(self, "Error", "k_party instance not created.")
            return
        
        if self.locc_operation_instance is None:
            QMessageBox.critical(self, "Error", "locc_operation instance not created.")
            return
        
        # Create locc_controller instance and execute protocol
        controller = locc_controller(self.locc_operation_instance, self.k_party_instance)
        controller.execute_protocol()
        QMessageBox.information(self, "Protocol Executed", "The protocol has been executed successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QuantumOperationsGUI()
    window.show()
    sys.exit(app.exec_())