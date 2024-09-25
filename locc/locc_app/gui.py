import sys
import os
import numpy as np
from qiskit import *
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import locc_controller
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

        self.k_party_controller = KPartyController(self)
        self.locc_protocol_controller = LoccProtocolController(self)
        self.execute_protocol_controller = None
        
        self.k_party_obj = None
        self.locc_protocol_obj = []
        self.party_list = []
        self.num_qudits_entries = []
        self.parties = []

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

        self.h_layout_top = QHBoxLayout()
        self.mode_button = QPushButton("Toggle Dark Mode")
        self.mode_button.clicked.connect(self.toggle_theme_mode)
        self.mode_button.setFixedSize(150, 25)
        self.h_layout_top.addWidget(self.mode_button)
        self.setStyleSheet(get_light_mode_stylesheet())

        self.add_input_param_file_button = QPushButton("Input Parameters Via .txt File")
        self.add_input_param_file_button.clicked.connect(self.on_input_param_file)
        self.h_layout_top.addWidget(self.add_input_param_file_button)

        self.scroll_layout.addLayout(self.h_layout_top)

        self.create_k_party_ui(self.scroll_layout)
        self.create_locc_operation_ui(self.scroll_layout)
        self.create_execution_ui(self.scroll_layout)
    
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

        self.quantum_state_label = QLabel("Please enter quantum state in form: <coefficient> |<basis state>| + <coefficient> |<basis state>| + ..., ex: 1/sqrt(2) |00000> + 1/sqrt(2) |11110>")
        self.quantum_state_label_comment = QLabel("Plese leave empty if you would like to start with ground state")
        self.quantum_state_entry = QLineEdit()
        layout.addWidget(self.quantum_state_label)
        layout.addWidget(self.quantum_state_label_comment)
        layout.addWidget(self.quantum_state_entry)


        h_layout2 = QHBoxLayout()
        self.party_names_entry = QLineEdit()
        h_layout2.addWidget(QLabel("Party Names (comma-separated):"))
        h_layout2.addWidget(self.party_names_entry)
        
        layout.addLayout(h_layout2)

        button_layout = QHBoxLayout()
        button_layout.addStretch() # stretch left
        create_k_party_button = QPushButton("Create K Party")
        create_k_party_button.setFixedSize(100, 25)
        button_layout.addWidget(create_k_party_button)
        button_layout.addStretch() # stretch right
        layout.addLayout(button_layout)
        # create_k_party_button.clicked.connect((self.k_party_controller).handle_create_k_party(self.party_names_entry.text(), self.k_entry.text(), self.dim_entry.text(), self.num_qudits_entries))
        create_k_party_button.clicked.connect(lambda: self.on_create_k_party(self.k_party_controller.handle_create_k_party(
        self.party_names_entry.text(), 
        self.k_entry.text(), 
        self.dim_entry.text(), 
        self.quantum_state_entry.text(),
        self.num_qudits_entries
            )
        ))
        
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

    def on_create_k_party(self, k_party_obj):
        self.k_party_obj = k_party_obj
        self.parties = self.k_party_obj.parties
    
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

        # Frame to hold LOCC entries
        self.locc_frame = QWidget()
        self.locc_frame_layout = QVBoxLayout(self.locc_frame)
        layout.addWidget(self.locc_frame)

        add_locc_button = QPushButton("Add LOCC Entries")
        # add_locc_button.clicked.connect(self.locc_protocol_controller.handle_add_locc_entries(self.locc_frame_layout, self.locc_entry.text()))
        add_locc_button.clicked.connect(self.on_add_locc_clicked)
        h_layout1.addWidget(add_locc_button)
        layout.addLayout(h_layout1)
    
    def on_add_locc_clicked(self):
        self.locc_protocol_obj = self.locc_protocol_controller.handle_add_locc_entries(self.locc_frame_layout, self.locc_entry.text())
        print(self.locc_protocol_obj)

    def create_execution_ui(self, layout):
        # Execution type and execution button
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        layout.addWidget(QLabel("Execution Specifics Creator"), alignment=Qt.AlignCenter)

        layout_execution_type = QHBoxLayout()
        execution_type_label = QLabel("Execution type:")
        layout_execution_type.addWidget(execution_type_label)
        
        self.select_execution_type = QComboBox()
        self.select_execution_type.addItems(["select execution type...", "upper bound", "lower bound"])
        layout_execution_type.addWidget(self.select_execution_type)

        layout.addLayout(layout_execution_type)

        party_layout_e_measures = QHBoxLayout()
        party_indicies_label = QLabel("Enter party index A and B for entanglement measures")
        self.party_A_box_entry = QLineEdit()
        self.party_B_box_entry = QLineEdit()
        party_layout_e_measures.addWidget(party_indicies_label)
        party_layout_e_measures.addWidget(self.party_A_box_entry)
        party_layout_e_measures.addWidget(self.party_B_box_entry)

        layout.addLayout(party_layout_e_measures)        

        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_measurement_scene)
        layout.addWidget(execute_button)

    def execute_measurement_scene(self):
        try:
            execution_type = self.select_execution_type.currentText()

            if execution_type == "select execution type...":
                raise ValueError("Please select execution type")
            if self.party_A_box_entry == "" or self.party_B_box_entry == "":
                raise ValueError("Please enter party indicies for entanglement measures")
            
            print(self.locc_protocol_obj)
            print(self.k_party_obj)
            self.execute_protocol_controller = ExecuteProtocolController(self.locc_protocol_obj, self.k_party_obj, execution_type, self.party_A_box_entry, self.party_A_box_entry)
            output_file, entanglement_measures, new_k_party_obj = self.execute_protocol_controller.execute_protocol()

            QMessageBox.information(self, "Protocol Executed", "The Protocol has been executed successfully. Please wait for the video to be generated.")

            self.video_thread = VideoThread(self.locc_protocol_obj, self.k_party_obj, output_file, entanglement_measures, execution_type, self.execute_protocol_controller.ee_string, new_k_party_obj)
            self.video_thread.start()
            self.video_thread.video_generated.connect(self.on_video_generated)
        
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

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
    
    def create_entanglement_measures(self):
        self.execution_type = self.select_execution_type.currentText()
        self.entanglement_measures = EntanglementMeasures(self.k_party_obj.dims, self.k_party_obj.q_state, party_to_measure=None)
        self.entanglement_measures.partyA = self.party_A_box_entry
        self.entanglement_measures.partyB = self.party_B_box_entry

        if self.execution_type == "upper bound":
            self.ee_string = self.entanglement_measures.get_le_upper_bound(self.k_party_obj, self.entanglement_measures.partyA, self.entanglement_measures.partyB)

        if self.execution_type == "lower bound":
            self.ee_string = self.entanglement_measures.get_le_lower_bound(self.k_party_obj, self.entanglement_measures.partyA, self.entanglement_measures.partyB)

    def toggle_theme_mode(self):
        if self.mode_button.text() == "Toggle Dark Mode":
            self.setStyleSheet(get_dark_mode_stylesheet())
            self.mode_button.setText("Toggle Light Mode")
        else:
            self.setStyleSheet(get_light_mode_stylesheet())
            self.mode_button.setText("Toggle Dark Mode")

    def on_input_param_file(self):
        print("TO DO: on input param file")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QuantumOperationsGUI()
    main_window.show()
    sys.exit(app.exec_())