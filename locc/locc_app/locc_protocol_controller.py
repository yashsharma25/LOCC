from k_party import KParty
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from qiskit.quantum_info import Statevector
from qiskit import *
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_operation import LoccOperation

class LoccProtocolController():
    def __init__(self, parent_gui):
        param = None
        self.parent_gui = parent_gui
        self.locc_step_widgets = []
        self.locc_protocol_obj = None
    
    def clear_layout(self, layout):
        """Recursively clear a layout and delete all its items."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # Ensure widgets are properly deleted
            elif item.layout() is not None:
                self.clear_layout(item.layout())  # Recursively clear nested layouts
            del item

    def handle_add_locc_entries(self, locc_frame_layout, locc_entry_text):
        while locc_frame_layout.count():
            item = locc_frame_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout is not None:
                self.clear_layout(item.layout())
            del item

        if locc_entry_text == '':
            QMessageBox.critical(
                self.parent_gui, "Input Error",
                "Please enter an integer value in 'Number of steps in LOCC protocol (number of locc objects)' field."
            )
            return
        
        try:
            num_steps = int(locc_entry_text)
        except ValueError:
            QMessageBox.critical(
                self.parent_gui, "Input Error",
                "Invalid input. Please enter a valid integer."
            )
            return
        
        self.locc_step_widgets.clear()

        # Dynamically add LOCC entries
        for i in range(num_steps):
            step_widgets = {}

            # Operation type selection
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel("Operation Type:"))
            operation_type_combobox = QComboBox()
            operation_type_combobox.addItems(["select operation type...", "measurement", "conditional"])
            h_layout.addWidget(operation_type_combobox)
            locc_frame_layout.addLayout(h_layout)
            step_widgets['operation_type_combobox'] = operation_type_combobox

            # Operator, party index, and qudit index
            operator_party_qudit_layout = QHBoxLayout()
            operator_party_qudit_layout.addWidget(QLabel("Operator"))
            operator_combobox = QComboBox()
            operator_combobox.addItems(["XGate", "HGate", "CXGate"])
            operator_party_qudit_layout.addWidget(operator_combobox)
            step_widgets['operator_combobox'] = operator_combobox

            party_index_entry = QLineEdit()
            operator_party_qudit_layout.addWidget(QLabel("Party Index:"))
            operator_party_qudit_layout.addWidget(party_index_entry)
            step_widgets['party_index_entry'] = party_index_entry

            qudit_index_entry = QLineEdit()
            operator_party_qudit_layout.addWidget(QLabel("Qudit Index:"))
            operator_party_qudit_layout.addWidget(qudit_index_entry)
            step_widgets['qudit_index_entry'] = qudit_index_entry

            locc_frame_layout.addLayout(operator_party_qudit_layout)

            # Conditional operation entries
            cond_text = QLabel("Please leave the below entries empty if this step is NOT a CONDITIONAL OPERATION.")
            cond_text.setAlignment(Qt.AlignCenter)
            locc_frame_layout.addWidget(cond_text)

            cond_h_layout = QHBoxLayout()
            condition_party_index_entry = QLineEdit()
            cond_h_layout.addWidget(QLabel("Condition Party Index"))
            cond_h_layout.addWidget(condition_party_index_entry)
            step_widgets['condition_party_index_entry'] = condition_party_index_entry

            condition_qudit_index_entry = QLineEdit()
            cond_h_layout.addWidget(QLabel("Condition Qudit Index"))
            cond_h_layout.addWidget(condition_qudit_index_entry)
            step_widgets['condition_qudit_index_entry'] = condition_qudit_index_entry

            condition_measurement_result_entry = QLineEdit()
            cond_h_layout.addWidget(QLabel("Condition Measurement Result"))
            cond_h_layout.addWidget(condition_measurement_result_entry)
            step_widgets['condition_measurement_result_entry'] = condition_measurement_result_entry

            locc_frame_layout.addLayout(cond_h_layout)

            # Save button for each step
            save_locc_entry_button = QPushButton("Save LOCC step entry")
            save_locc_entry_button.clicked.connect(lambda _, w=step_widgets: self.save_locc_entry(w))
            locc_frame_layout.addWidget(save_locc_entry_button)

            # Spacer after each step
            spacer_2 = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
            locc_frame_layout.addSpacerItem(spacer_2)

            # Add step widgets to the list
            self.locc_step_widgets.append(step_widgets)

    def save_locc_entry(self, widgets):
        # Ensure the list is always initialized before appending
        if self.locc_protocol_obj is None:
            self.locc_protocol_obj = []

        try:
            # Extract values from widgets
            party_index = int(widgets['party_index_entry'].text())
            qudit_index = int(widgets['qudit_index_entry'].text())
            operation_type = widgets['operation_type_combobox'].currentText()

            operator = None
            condition = None

            # Handle conditional operations
            if operation_type == "conditional":
                condition_party_index = int(widgets['condition_party_index_entry'].text())
                condition_qudit_index = int(widgets['condition_qudit_index_entry'].text())
                condition_measurement_result = int(widgets['condition_measurement_result_entry'].text())
                condition = (condition_party_index, condition_qudit_index, condition_measurement_result)

                operator_choice = widgets['operator_combobox'].currentText()
                if operator_choice == "XGate":
                    operator = XGate()
                elif operator_choice == "HGate":
                    operator = HGate()
                elif operator_choice == "CXGate":
                    operator = CXGate()

            elif operation_type == "measurement":
                operator_choice = widgets['operator_combobox'].currentText()
                if operator_choice == "XGate":
                    operator = XGate()
                elif operator_choice == "HGate":
                    operator = HGate()
                elif operator_choice == "CXGate":
                    operator = CXGate()

            # Create LOCC operation instance
            locc_op = LoccOperation(party_index, qudit_index, operation_type, operator, condition)

            # Save to the list
            self.locc_protocol_obj.append(locc_op)

            # Confirmation message - Pass parent_gui instead of self
            QMessageBox.information(
                self.parent_gui, "LOCC Operation", 
                f"LOCC Operation Created:\nParty Index: {locc_op.party_index}\nQudit Index: {locc_op.qudit_index}\nOperation Type: {locc_op.operation_type}\nCondition: {locc_op.condition}\nOperator: {locc_op.operator}"
            )

            return self.locc_protocol_obj

        except ValueError:
            # Error message - Also pass parent_gui instead of self
            QMessageBox.critical(self.parent_gui, "Input Error", "Please enter valid integer values.")
