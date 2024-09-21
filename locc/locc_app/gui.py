import sys
import os
import numpy as np
from qiskit import *
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import LoccController
from k_party import KParty
from locc_operation import LoccOperation
from entanglement_measures import EntanglementMeasures
from video_thread import VideoThread
from themes import get_dark_mode_stylesheet, get_light_mode_stylesheet
from k_party_controller import KPartyController
from locc_protocol_controller import LoccProtocolController
from execute_protocol_controller import ExecuteProtocolController
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *

os.environ["QT_QPA_PLATFORM"] = "xcb" # to fix qt.qpa.wayland: Wayland does not support QWindow::requestActivate() issue

class QuantumOperationsGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quantum Operations")
        self.setGeometry(1000, 800, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        self.mode_button = QPushButton("Toggle Dark Mode")
        self.mode_button.clicked.connect(self.toggle_mode)
        self.mode_button.setFixedSize(150, 25)
        self.scroll_layout.addWidget(self.mode_button)
        self.setStyleSheet(get_light_mode_stylesheet())

        self.create_k_party_ui(self.scroll_layout)
        
        self.create_locc_operation_ui(self.scroll_layout)

        self.locc_protocol_controller = LoccProtocolController()
        self.execute_protocol_controller = ExecuteProtocolController()
        
        self.k_party_obj = None
        self.locc_protocol_obj = []
        self.party_list = []
        self.num_qudits_entries = []
    
    def create_k_party_ui(self, layout):
        layout.addWidget(QLabel("K Party Creator"), alignment=Qt.AlignCenter)

        h_layout1 = QHBoxLayout()
        self.k_entry = QLineEdit()
        h_layout1.addWidget(QLabel("Number of Parties (k):"))
        h_layout1.addWidget(self.k_entry)

        self.dim_entry = QLineEdit()
        h_layout1.addWidget(QLabel("Dimension of Qudit(s):"))
        h_layout1.addWidget(self.dim_entry)

        add_party_button = QPushButton("Add Party Entries")
        add_party_button.clicked.connect(self.add_party_entries_ui)
        h_layout1.addWidget(add_party_button)

        layout.addLayout(h_layout1)

        self.party_frame = QWidget()
        self.party_frame_layout = QVBoxLayout(self.party_frame)
        layout.addWidget(self.party_frame)

        h_layout2 = QHBoxLayout()
        self.party_names_entry = QLineEdit()
        h_layout2.addWidget(QLabel("Party Names (comma-separated):"))
        h_layout2.addWidget(self.party_names_entry)
        
        layout.addLayout(h_layout2)

        button_layout = QHBoxLayout()
        button_layout.addStretch() # stretch left
        create_k_party_button = QPushButton("Create K Party")
        self.k_party_controller = KPartyController(self)
        # create_k_party_button.clicked.connect((self.k_party_controller).handle_create_k_party(self.party_names_entry.text(), self.k_entry.text(), self.dim_entry.text(), self.num_qudits_entries))
        create_k_party_button.clicked.connect(lambda: self.k_party_controller.handle_create_k_party(
        self.party_names_entry.text(), 
        self.k_entry.text(), 
        self.dim_entry.text(), 
        self.num_qudits_entries
        ))

        create_k_party_button.setFixedSize(100, 25)
        button_layout.addWidget(create_k_party_button)
        button_layout.addStretch() # stretch right
        layout.addLayout(button_layout)

    def add_party_entries_ui(self):
        for i in reversed(range(self.party_frame_layout.count())): 
            self.party_frame_layout.itemAt(i).widget().setParent(None)
        
        if self.k_entry.text() == '' or self.dim_entry.text() == '':
            QMessageBox.critical(self, "Input Error", "Please enter an integer value in 'Number of Parties (k) field' and 'Dimension fo Qudit(s)' field.")
            return

        k = int(self.k_entry.text())
        for i in range(k):
            self.party_frame_layout.addWidget(QLabel(f"Number of Qudits for Party {i+1}:"))
            num_qudits_entry = QLineEdit()
            self.party_frame_layout.addWidget(num_qudits_entry)
            self.num_qudits_entries.append(num_qudits_entry)
    
    def create_locc_operation_ui(self, layout):
        # Initial setup and UI components
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        layout.addWidget(QLabel("LOCC Operation Creator"), alignment=Qt.AlignCenter)

        # Input for the number of LOCC steps
        h_layout1 = QHBoxLayout()
        self.locc_entry = QLineEdit()
        h_layout1.addWidget(QLabel("Number of steps in LOCC protocol (number of locc objects):"))
        h_layout1.addWidget(self.locc_entry)

        add_locc_button = QPushButton("Add LOCC Entries")
        add_locc_button.clicked.connect(self.add_locc_entries)
        h_layout1.addWidget(add_locc_button)

        layout.addLayout(h_layout1)

        # Frame to hold LOCC entries
        self.locc_frame = QWidget()
        self.locc_frame_layout = QVBoxLayout(self.locc_frame)
        layout.addWidget(self.locc_frame)

        # Execution type and execution button
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        execution_type_label = QLabel("Execution type:")
        layout.addWidget(execution_type_label)
        
        self.select_execution_type = QComboBox()
        self.select_execution_type.addItems(["select execution type...", "upper bound", "lower bound"])
        layout.addWidget(self.select_execution_type)

        self.party_list = self.party_names_entry.text().split(',') if self.party_names_entry.text() else []
        
        listA = ["select party A for entanglement measures"]
        listA.extend(self.party_list)
        self.select_party_A = QComboBox()
        self.select_party_A.addItems(listA)
        
        listB = ["select party B for entanglement measures"]
        listB.extend(self.party_list)
        self.select_party_B = QComboBox()
        self.select_party_B.addItems(self.party_list)
        layout.addWidget(self.select_party_A)
        layout.addWidget(self.select_party_B)

        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_measurement_scene)
        layout.addWidget(execute_button)

        # List to keep track of widget sets for each step
        self.locc_step_widgets = []

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

    def add_locc_entries(self):
        # Clear existing entries in the layout
        while self.locc_frame_layout.count():
            item = self.locc_frame_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())
            del item

        # Check for valid integer input
        if self.locc_entry.text() == '':
            QMessageBox.critical(
                self, "Input Error", 
                "Please enter an integer value in 'Number of steps in LOCC protocol (number of locc objects) field'"
            )
            return

        try:
            num_steps = int(self.locc_entry.text())
        except ValueError:
            QMessageBox.critical(
                self, "Input Error", 
                "Invalid input. Please enter a valid integer."
            )
            return

        # Clear any existing step widgets information
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
            self.locc_frame_layout.addLayout(h_layout)
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

            self.locc_frame_layout.addLayout(operator_party_qudit_layout)

            # Conditional operation entries
            cond_text = QLabel("Please leave the below entries empty if this step is NOT a CONDITIONAL OPERATION.")
            cond_text.setAlignment(Qt.AlignCenter)
            self.locc_frame_layout.addWidget(cond_text)

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

            self.locc_frame_layout.addLayout(cond_h_layout)

            # Save button for each step
            save_locc_entry_button = QPushButton("Save LOCC step entry")
            save_locc_entry_button.clicked.connect(lambda _, w=step_widgets: self.save_locc_entry(w))
            self.locc_frame_layout.addWidget(save_locc_entry_button)

            # Spacer after each step
            spacer_2 = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.locc_frame_layout.addSpacerItem(spacer_2)

            # Add step widgets to the list
            self.locc_step_widgets.append(step_widgets)
        
    # TO USE USERS INTERNAL OS VIDEO PLAYER
    @pyqtSlot(str)
    def on_video_generated(self, video_path):
        if not os.path.exists(video_path):
            QMessageBox.critical(self, "Error", f"Video file {video_path} not found.")
            return
        
        if sys.platform.startswith('darwin'): # macOS
            QProcess.startDetached("open", [video_path])
        elif sys.platform.startswith('win'): # windows
            os.startFile(video_path)
        else: # linux, other unix-like operating systems
            QProcess.startDetached("xdg-open", [video_path])

    def toggle_mode(self):
        if self.mode_button.text() == "Toggle Dark Mode":
            self.setStyleSheet(get_dark_mode_stylesheet())
            self.mode_button.setText("Toggle Light Mode")
        else:
            self.setStyleSheet(get_light_mode_stylesheet())
            self.mode_button.setText("Toggle Dark Mode")

    def execute_measurement_scene(self):
        if self.k_party_obj is None:
            QMessageBox.critical(self, "Error", "K Party instance not created.")
            return
        if self.locc_protocol_obj is None:
            QMessageBox.critical(self, "Error", "LOCC Operation instance not created.")
            return
        if self.select_execution_type.currentText() == "select execution type...":
            QMessageBox.critical(self, "Error", "Please select execution type")
            return
        if self.select_party_A.currentText() == "select party A for entanglement measures":
            QMessageBox.critical(self, "Error", "Please select part for A entanglement measures")
            return
        
        if self.select_party_B.currentText() == "select party B for entanglement measures":
            QMessageBox.critical(self, "Error", "Please select part for B entanglement measures")
            return
        
        if self.select_party_A.currentText() == self.select_party_B.currentText():
            QMessageBox.critical(self, "Error", "Please ensure party A and party B are different for entanglement measures.")
            return
        
        controller = LoccController(self.locc_protocol_obj, self.k_party_obj)
        res = controller.execute_protocol()
        # res[0] = a string describing outcome, and res[1] = k_party_obj itself (now updated with measurement outcome)
        # notice how actual computation and controller for the program has already happend before generating the video

        # array of k_party_objects arr, PartyA, PartyB -- needed for EntanglementMeasures object
        self.create_entanglement_measures()

        output_file = "measurement_scene.mp4"

        QMessageBox.information(self, "Protocol Executed", "The Protocol has been executed successfully. Please wait for video to generated.")
            
        self.video_thread = VideoThread(self.locc_protocol_obj, self.k_party_obj, output_file, res, self.execution_type, self.ee_string) # create the video_thread instance, feed params
        self.video_thread.start() # start the thread, now that video thread instance is created and system video player is connected
        self.video_thread.video_generated.connect(self.on_video_generated) # connect the system video player

    def create_entanglement_measures(self):
        self.execution_type = self.select_execution_type.currentText()
        self.entanglement_measures = EntanglementMeasures(self.k_party_obj.dims, self.k_party_obj.q_state, party_to_measure=None)
        self.entanglement_measures.partyA = self.parties[self.select_party_A.currentText()]
        self.entanglement_measures.partyB = self.parties[self.select_party_B.currentText()]

        if self.execution_type == "upper bound":
            self.ee_string = self.entanglement_measures.get_le_upper_bound(self.k_party_obj, self.entanglement_measures.partyA, self.entanglement_measures.partyB)

        if self.execution_type == "lower bound":
            self.ee_string = self.entanglement_measures.get_le_lower_bound(self.k_party_obj, self.entanglement_measures.partyA, self.entanglement_measures.partyB)
    
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

            # Confirmation message
            QMessageBox.information(
                self, "LOCC Operation", 
                f"LOCC Operation Created:\nParty Index: {locc_op.party_index}\nQudit Index: {locc_op.qudit_index}\nOperation Type: {locc_op.operation_type}\nCondition: {locc_op.condition}\nOperator: {locc_op.operator}"
            )

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid integer values.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QuantumOperationsGUI()
    main_window.show()
    sys.exit(app.exec_())