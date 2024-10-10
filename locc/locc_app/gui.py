import sys
import os
import time
import shutil
from qiskit import *
from k_party_controller import k_party_controller
from locc_protocol_controller import LoccProtocolController
from locc_controller import locc_controller
from video_thread import VideoThread
from themes import get_dark_mode_stylesheet, get_light_mode_stylesheet
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog

os.environ["QT_QPA_PLATFORM"] = "xcb" # to fix qt.qpa.wayland: Wayland does not support QWindow::requestActivate() issue

class QuantumOperationsGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.k_party_controller = k_party_controller(self)
        self.locc_protocol_controller = LoccProtocolController(self)
        self.execute_protocol_controller = None
        
        self.k_party_obj = None
        self.locc_protocol_obj = []
        self.party_list = []
        self.num_qudits_entries = []
        self.party_dim_entries = []

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
        self.mode_button = QPushButton("Toggle Light Mode")
        self.mode_button.clicked.connect(self.toggle_theme_mode)
        self.mode_button.setFixedSize(150, 25)
        self.h_layout_top.addWidget(self.mode_button)
        self.setStyleSheet(get_dark_mode_stylesheet())

        self.add_input_param_file_button = QPushButton("Input Parameters Via .txt File")
        self.add_input_param_file_button.clicked.connect(self.on_input_param_file)
        self.h_layout_top.addWidget(self.add_input_param_file_button)

        self.download_template_button = QPushButton("Download Parameter Template")
        self.download_template_button.clicked.connect(self.download_template)
        self.h_layout_top.addWidget(self.download_template_button)


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
        create_k_party_button.clicked.connect(lambda: self.on_create_k_party(self.k_party_controller.handle_create_k_party(
        self.party_names_entry.text(), 
        self.k_entry.text(),
        self.quantum_state_entry.text(),
        self.num_qudits_entries,
        self.party_dim_entries
            )
        ))
        
    def add_party_entries_ui(self):
        for i in reversed(range(self.party_frame_layout.count())): 
            self.party_frame_layout.itemAt(i).widget().setParent(None)
        
        if self.k_entry.text() == '':
            QMessageBox.critical(self, "Input Error", "Please enter an integer value in 'Number of Parties (k) field' and 'Dimension fo Qudit(s)' field.")
            return

        k = int(self.k_entry.text())
        for i in range(k):
            self.party_frame_layout.addWidget(QLabel(f"Number of Qudits for Party {i+1}:"))
            num_qudits_entry = QLineEdit()
            self.party_frame_layout.addWidget(num_qudits_entry)
            self.num_qudits_entries.append(num_qudits_entry)

            self.party_frame_layout.addWidget(QLabel(f"Dimension of Qudit for Party {i+1} (d = ?):"))
            party_dim_entry = QLineEdit()
            self.party_frame_layout.addWidget(party_dim_entry)
            self.party_dim_entries.append(party_dim_entry)

    def on_create_k_party(self, k_party_obj):
        self.k_party_obj = k_party_obj
        print(f"K party object created. Dims = {k_party_obj.dims} state_desc = {k_party_obj.state_desc} q_state = {k_party_obj.q_state} party_names = {k_party_obj.party_names}")
        
    def create_locc_operation_ui(self, layout):
        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout(self.header_widget)

        self.header_layout.addWidget(QLabel("LOCC Operation Creator"), alignment=Qt.AlignCenter)
        h_layout1 = QHBoxLayout()
        self.locc_entry = QLineEdit()
        h_layout1.addWidget(QLabel("Number of steps in LOCC protocol (number of locc objects):"))
        h_layout1.addWidget(self.locc_entry)

        add_locc_button = QPushButton("Add LOCC Entries")
        add_locc_button.clicked.connect(self.on_add_locc_clicked)
        h_layout1.addWidget(add_locc_button)

        self.header_layout.addLayout(h_layout1)

        layout.addWidget(self.header_widget)

        self.locc_frame = QWidget()
        self.locc_frame_layout = QVBoxLayout(self.locc_frame)
        layout.addWidget(self.locc_frame)

    def on_add_locc_clicked(self):
        locc_protocol_result = self.locc_protocol_controller.handle_add_locc_entries(self.locc_frame_layout, self.locc_entry.text())
        
        if locc_protocol_result is not None:
            self.locc_protocol_obj = locc_protocol_result
            print(f"locc_protocol_obj = {self.locc_protocol_obj}")
        else:
            print("Error: Failed to create LOCC protocol.")


    def create_execution_ui(self, layout):
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        layout.addWidget(QLabel("Execution Specifics Creator"), alignment=Qt.AlignCenter)

        layout_execution_type = QHBoxLayout()
        execution_type_label = QLabel("Localisable Entanglement Metric:")
        layout_execution_type.addWidget(execution_type_label)
        
        self.select_execution_type = QComboBox()
        self.select_execution_type.addItems(["select execution type...", "upper bound", "lower bound"])
        layout_execution_type.addWidget(self.select_execution_type)

        layout.addLayout(layout_execution_type)

        '''
        party_layout_e_measures = QHBoxLayout()
        party_indicies_label = QLabel("Enter party index A and B for entanglement measures")
        self.party_A_box_entry = QLineEdit()
        self.party_B_box_entry = QLineEdit()
        party_layout_e_measures.addWidget(party_indicies_label)
        party_layout_e_measures.addWidget(self.party_A_box_entry)
        party_layout_e_measures.addWidget(self.party_B_box_entry)

        layout.addLayout(party_layout_e_measures)        
        '''

        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_measurement_scene)
        layout.addWidget(execute_button)

    def execute_measurement_scene(self):
        try:
            execution_type = self.select_execution_type.currentText()

            if execution_type == "select execution type...":
                raise ValueError("Please select execution type")
            '''
            if self.party_A_box_entry == "" or self.party_B_box_entry == "":
                raise ValueError("Please enter party indicies for entanglement measures")
            '''

            if not self.locc_protocol_obj or not self.k_party_obj:
                raise ValueError("LOCC Operation or K Party instance not created.")
            
            print(self.locc_protocol_obj)
            print(self.k_party_obj)

            QMessageBox.information(self, "Protocol Execution Started", "Protocol execution has begun. Please wait for the video to be generated.")

            self.video_thread = VideoThread(self.locc_protocol_obj, self.k_party_obj, "measurement_scene.mp4", execution_type)
            self.video_thread.video_generated.connect(self.on_video_generated)
            self.video_thread.new_k_party_generated.connect(self.on_new_k_party_generated)
            self.video_thread.start()
        
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    @pyqtSlot(object)
    def on_new_k_party_generated(self, new_k_party_obj):
        self.new_k_party_obj = new_k_party_obj
        QMessageBox.information(self, "Protocol Execution Successful", "New k party object received and updated.")
    
    # TO USE USERS INTERNAL OS VIDEO PLAYER
    @pyqtSlot(str)
    def on_video_generated(self, video_path):
        '''
        if not os.path.exists(video_path):
            QMessageBox.critical(self, "Error", f"Video file {video_path} not found.")
            return
        '''

        if sys.platform.startswith('darwin'): # macOS
            QProcess.startDetached("open", [video_path])
        elif sys.platform.startswith('win'): # windows
            os.startFile(video_path)
        else: # linux, other unix-like operating systems
            QProcess.startDetached("xdg-open", [video_path])

    def toggle_theme_mode(self):
        if self.mode_button.text() == "Toggle Dark Mode":
            self.setStyleSheet(get_dark_mode_stylesheet())
            self.mode_button.setText("Toggle Light Mode")
        else:
            self.setStyleSheet(get_light_mode_stylesheet())
            self.mode_button.setText("Toggle Dark Mode")

    def on_input_param_file(self):
        QMessageBox.information(self, "Input Parameter File", "Will be implemented in V2!")
        '''
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Parameter File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            try:
                params = {}
                with open(file_name, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or ":" not in line:
                            continue
                        param_name, param_value = map(str.strip, line.split(":", 1))
                        params[param_name] = param_value

                k_value = params.get("Number of Parties (k)", "")
                self.k_entry.setText(k_value)

                if k_value.isdigit():
                    self.add_party_entries_ui()
                    self.k_entry.setText(k_value)
                self.party_names_entry.setText(params.get("Party Names", ""))
                self.quantum_state_entry.setText(params.get("Quantum State", ""))
                
                qudits = params.get("Number of Qudits", "")
                if qudits:
                    qudits_list = qudits.split(",")
                    for i, qudit_entry in enumerate(self.num_qudits_entries):
                        if i < len(qudits_list):
                            qudit_entry.setText(qudits_list[i])

                dims = params.get("Party Dimensions", "")
                if dims:
                    dims_list = dims.split(",")
                    for i, dim_entry in enumerate(self.party_dim_entries):
                        if i < len(dims_list):
                            dim_entry.setText(dims_list[i])

                locc_steps_value = params.get("Number of LOCC Steps", "")
                self.locc_entry.setText(locc_steps_value)

                # Trigger LOCC entry addition based on the number of LOCC steps
                if locc_steps_value.isdigit():
                    self.handle_add_locc_entries(self.locc_frame_layout, locc_steps_value)

                self.select_execution_type.setCurrentText(params.get("Execution Type", ""))
                self.party_A_box_entry.setText(params.get("Party A", ""))
                self.party_B_box_entry.setText(params.get("Party B", ""))

                QMessageBox.information(self, "Success", "Parameters loaded successfully!")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load parameters: {str(e)}")
        '''

    def download_template(self):
        QMessageBox.information(self, "Download Parameter Template", "Will be implemented in V2!")
        '''
        # Create the content of the template
        template_content = """Example input:
    Number of Parties (k): 3
    Party Names: Alice,Bob,Charlie
    Quantum State: 1/sqrt(2) |00> + 1/sqrt(2) |11>
    Number of Qudits: 2,3,4
    Party Dimensions: 2,2,3
    Number of LOCC Steps: 5
    Execution Type: upper bound
    Party A: 1
    Party B: 2

    Please enter relevant information below:
    Number of Parties (k):
    Party Names:
    Quantum State:
    Number of Qudits:
    Party Dimensions:
    Number of LOCC Steps:
    Execution Type:
    Party A:
    Party B:
    """

        # Ask the user where to save the file
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Template As", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if save_path:
            # Save the file
            try:
                with open(save_path, 'w') as template_file:
                    template_file.write(template_content)
                QMessageBox.information(self, "Template Saved", f"Template successfully saved to {save_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save the template file: {str(e)}")
        '''


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QuantumOperationsGUI()
    main_window.show()
    sys.exit(app.exec_())