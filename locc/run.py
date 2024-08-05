import sys
import os
import numpy as np
from qiskit import *
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import locc_controller
from k_party import k_party
from locc_operation import locc_operation
from entanglement_measures import EntanglementMeasures
from manim import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
import copy

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

        # Add mode toggle button to switch themes
        self.mode_button = QPushButton("Toggle Dark Mode")
        self.mode_button.clicked.connect(self.toggle_mode)
        self.mode_button.setFixedSize(150, 25)
        self.scroll_layout.addWidget(self.mode_button)
        self.set_light_mode()

        # k party obj ui
        self.create_k_party_ui(self.scroll_layout)
        
        # locc op obj ui
        self.create_locc_operation_ui(self.scroll_layout)

        self.k_party_instance = None
        self.locc_operation_instance = None
    
    # K PARTY UI
    def create_k_party_ui(self, layout):
        layout.addWidget(QLabel("K Party Creator"), alignment=Qt.AlignCenter)

        h_layout1 = QHBoxLayout()
        self.k_entry = QLineEdit()
        h_layout1.addWidget(QLabel("Number of Parties (k):"))
        h_layout1.addWidget(self.k_entry)

        add_party_button = QPushButton("Add Party Entries")
        add_party_button.clicked.connect(self.add_party_entries)
        h_layout1.addWidget(add_party_button)

        layout.addLayout(h_layout1)

        self.party_frame = QWidget()
        self.party_frame_layout = QVBoxLayout(self.party_frame)
        layout.addWidget(self.party_frame)

        h_layout2 = QHBoxLayout()
        self.party_names_entry = QLineEdit()
        h_layout2.addWidget(QLabel("Party Names (comma-separated, optional):"))
        h_layout2.addWidget(self.party_names_entry)
        
        layout.addLayout(h_layout2)

        button_layout = QHBoxLayout()
        button_layout.addStretch() # stretch left
        create_k_party_button = QPushButton("Create K Party")
        create_k_party_button.clicked.connect(self.create_k_party)
        create_k_party_button.setFixedSize(100, 25)
        button_layout.addWidget(create_k_party_button)
        button_layout.addStretch() # stretch right
        layout.addLayout(button_layout)

    def add_party_entries(self):
        for i in reversed(range(self.party_frame_layout.count())): 
            self.party_frame_layout.itemAt(i).widget().setParent(None)
        
        self.num_qudits_entries = []
        self.qudit_dims_entries = []
        
        if self.k_entry.text() == '':
            QMessageBox.critical(self, "Input Error", "Please enter an integer value in 'Number of Parties (k) field'")
            return

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
            QMessageBox.critical(self, "Input Error", "Please ensure all entries are integer values.")

    def create_initial_state(self, dims):
        return Statevector.from_label('0' * dims)
    


    
    # LOCC UI
    def create_locc_operation_ui(self, layout):
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        layout.addWidget(QLabel("LOCC Operation Creator"), alignment=Qt.AlignCenter)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Operation Type:"))
        self.operation_type_combobox = QComboBox()
        self.operation_type_combobox.addItems(["select operation type...", "measurement", "conditional"])
        h_layout.addWidget(self.operation_type_combobox)

        set_op_type_specifics_button = QPushButton("Set Operation Type Specifics")
        set_op_type_specifics_button.clicked.connect(lambda: self.set_operation_type_specifics(layout))
        set_op_type_specifics_button.setFixedSize(500, 25)
        h_layout.addWidget(set_op_type_specifics_button)
        layout.addLayout(h_layout)

        self.locc_op_additonal_widgets = [] # to keep track of dynamically added widgets

        # self.operation_type_combobox.currentIndexChanged.connect(lambda: self.on_operation_combo_changed(layout))
    
    def set_operation_type_specifics(self, layout):
        # quick check to make sure that the user selected an operation type
        if self.operation_type_combobox.currentText() == "select operation type...":
            QMessageBox.critical(self, "Error", "Please select operation type")
            return
        # remove previously added widgets
        for widget in self.locc_op_additonal_widgets:
            layout.removeWidget(widget)
            widget.deleteLater()
        self.locc_op_additonal_widgets.clear()

        selected_text = self.operation_type_combobox.currentText()
        
        if selected_text == "measurement":
            operator_label = QLabel("Operator")
            layout.addWidget(operator_label)
            self.operator_combobox = QComboBox()
            self.operator_combobox.addItems(["XGate", "HGate", "CXGate"])
            layout.addWidget(self.operator_combobox)
            self.locc_op_additonal_widgets.append(operator_label)
            self.locc_op_additonal_widgets.append(self.operator_combobox)

        elif selected_text == "conditional":
            operator_label = QLabel("Operator")
            layout.addWidget(operator_label)
            self.operator_combobox = QComboBox()
            self.operator_combobox.addItems(["XGate", "HGate", "CXGate"])
            layout.addWidget(self.operator_combobox)
            self.locc_op_additonal_widgets.append(operator_label)
            self.locc_op_additonal_widgets.append(self.operator_combobox)

            self.condition_party_index_entry = QLineEdit()
            cond_party_index_label = QLabel("Condition Party Index")
            layout.addWidget(cond_party_index_label)
            layout.addWidget(self.condition_party_index_entry)
            self.locc_op_additonal_widgets.append(cond_party_index_label)
            self.locc_op_additonal_widgets.append(self.condition_party_index_entry)

            self.condition_qudit_index_entry = QLineEdit()
            cond_qudit_index_label = QLabel("Condition Qudit Index")
            layout.addWidget(cond_qudit_index_label)
            layout.addWidget(self.condition_qudit_index_entry)
            self.locc_op_additonal_widgets.append(cond_qudit_index_label)
            self.locc_op_additonal_widgets.append(self.condition_qudit_index_entry)

            self.condition_measurement_result_entry = QLineEdit()
            cond_m_res_label = QLabel("Condition Measurement Result")
            layout.addWidget(cond_m_res_label)
            layout.addWidget(self.condition_measurement_result_entry)
            self.locc_op_additonal_widgets.append(cond_m_res_label)
            self.locc_op_additonal_widgets.append(self.condition_measurement_result_entry)

        self.party_index_entry = QLineEdit()
        party_index_label = QLabel("Party Index:")
        layout.addWidget(party_index_label)
        layout.addWidget(self.party_index_entry)
        self.locc_op_additonal_widgets.append(party_index_label)
        self.locc_op_additonal_widgets.append(self.party_index_entry)


        self.qudit_index_entry = QLineEdit()
        qudit_index_label = QLabel("Qudit Index:")
        layout.addWidget(qudit_index_label)
        layout.addWidget(self.qudit_index_entry)
        self.locc_op_additonal_widgets.append(qudit_index_label)
        self.locc_op_additonal_widgets.append(self.qudit_index_entry)

        create_locc_button = QPushButton("Create LOCC Operation")
        create_locc_button.clicked.connect(self.create_locc_operation)
        # create_locc_button.setEnabled(False) # initially disable the button
        layout.addWidget(create_locc_button)
        self.locc_op_additonal_widgets.append(create_locc_button)

        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addSpacerItem(self.spacer)
        execution_type_label = QLabel("Execution type:")
        layout.addWidget(execution_type_label)
        self.select_execution_type = QComboBox()
        self.select_execution_type.addItems(["select execution type...", "upper bound", "lower bound"])
        layout.addWidget(self.select_execution_type)
        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_measurement_scene)
        layout.addWidget(execute_button)
        self.locc_op_additonal_widgets.append(execute_button)

    def create_locc_operation(self):
        try:
            party_index = int(self.party_index_entry.text())
            qudit_index = int(self.qudit_index_entry.text())
            operation_type = self.operation_type_combobox.currentText()
            
            operator = None
            condition = None
            
            if operation_type == "conditional":
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
            
            elif operation_type == "measurement":
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
    
    
    # THEMES
    def set_light_mode(self):
        self.light_mode_stylesheet = """
        QWidget {
            background-color: white;
            color: black;
        }
        QPushButton {
            background-color: lightgray;
            color: black;
        }
        QLineEdit {
            background-color: white;
            color: black;
        }
        QLabel {
            color: black;
        }
        QScrollArea {
            background-color: white;
        }
        QSlider::groove:horizontal {
            background: lightgray;
        }
        QSlider::handle:horizontal {
            background: darkgray;
        }
        """
        self.setStyleSheet(self.light_mode_stylesheet)

    def set_dark_mode(self):
        self.dark_mode_stylesheet = """
        QWidget {
            background-color: #2E2E2E;
            color: white;
        }
        QPushButton {
            background-color: #444444;
            color: white;
        }
        QLineEdit {
            background-color: #555555;
            color: white;
        }
        QLabel {
            color: white;
        }
        QScrollArea {
            background-color: #2E2E2E;
        }
        QSlider::groove:horizontal {
            background: #555555;
        }
        QSlider::handle:horizontal {
            background: #777777;
        }
        """
        self.setStyleSheet(self.dark_mode_stylesheet)

    def toggle_mode(self):
        if self.mode_button.text() == "Toggle Dark Mode":
            self.set_dark_mode()
            self.mode_button.setText("Toggle Light Mode")
        else:
            self.set_light_mode()
            self.mode_button.setText("Toggle Dark Mode")

    def execute_measurement_scene(self):
        if self.k_party_instance is None:
            QMessageBox.critical(self, "Error", "K Party instance not created.")
            return
        if self.locc_operation_instance is None:
            QMessageBox.critical(self, "Error", "LOCC Operation instance not created.")
            return
        if self.select_execution_type.currentText() == "select execution type...":
            QMessageBox.critical(self, "Error", "Please select execution type")
            return
        
        self.execution_type = self.select_execution_type.currentText()
        controller = locc_controller(self.locc_operation_instance, self.k_party_instance)
        res = controller.execute_protocol()
        # res[0] = a string describing outcome, and res[1] = k_party_obj itself (now updated with measurement outcome)
        # notice how actual computation and controller for the program has already happend before generating the video

        # array of k_party_objects arr, PartyA, PartyB -- needed for EntanglementMeasures object
        self.entanglement_measures = EntanglementMeasures(self.k_party_instance.dims, self.k_party_instance.q_state, party_to_measure=None)
        # what do N, psi, party_to_measure attributes in EntanglementMeasures object mean?
        
        output_file = "measurement_scene.mp4"

        QMessageBox.information(self, "Protocol Executed", "The Protocol has been executed successfully. Please wait for video to generated.")
            
        self.video_thread = VideoThread(self.locc_operation_instance, self.k_party_instance, output_file, res, self.execution_type, self.entanglement_measures) # create the video_thread instance, feed params
        self.video_thread.start() # start the thread, now that video thread instance is created and system video player is connected
        self.video_thread.video_generated.connect(self.on_video_generated) # connect the system video player

class VideoThread(QThread):
    video_generated = pyqtSignal(str)

    def __init__(self, locc_operations, k_party, output_file, res, execution_type, entanglement_measures):
        super().__init__()
        self.locc_operations = locc_operations
        self.k_party = k_party
        self.output_file = output_file
        self.res = res
        self.execution_type = execution_type
        self.entanglement_measures = entanglement_measures

    def run(self):
        MeasurementScene(self.locc_operations, self.k_party, self.res, self.execution_type, self.entanglement_measures).render(self.output_file)
        self.video_generated.emit(self.output_file)

# MANIM SCRIPT
class MeasurementScene(ThreeDScene):
    def __init__(self, locc_op, k_party_obj, res, execution_type, entanglement_measures, **kwargs):
        self.locc_op = locc_op
        self.k_party_obj = k_party_obj
        self.res = res
        self.execution_type = execution_type
        self.entanglement_measures = entanglement_measures
        super().__init__(**kwargs)

    def construct(self):
        # create the graph: exisiting manim stuff
        # show the measurement happening: controller.execute_protocol()
        # show the result of the measurement: get_le_upper_bound_evolving()
        self.create_graph()
        # at this point, the graph is completely created
        # self.model_measurement()
        self.model_individual_EEs()

    def create_graph(self):
        # basic labels
        my_text = Text(f"Executing {self.locc_op[0].operation_type} on party {self.locc_op[0].party_index}, qudit {self.locc_op[0].qudit_index}")
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))
        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)

        # create nodes and edges
        party_one = self.k_party_obj.state_desc[0] # VERY IMPORTANT!! UNDERSTAND STATE_DESC ATTRIBUTE -- ATM HARD CODED FOR ONE PARTY
        num_qudits = party_one[0]
        nodes = [Sphere(radius=0.3, color=BLUE) for _ in range(num_qudits)]
        coordinates = [(2 * np.cos(angle), 2 * np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, num_qudits, endpoint=False)]

        for node, coord in zip(nodes, coordinates):
            node.move_to(coord)

        node_dots = [Dot(point=coord) for coord in coordinates]
        
        # initialize edges
        edges, self.edge_map = [], {}
        for i in range(num_qudits):
            for j in range(i + 1, num_qudits):
                if (j, i) not in self.edge_map:
                    edge = Line(node_dots[i].get_center(), node_dots[j].get_center())
                    self.edge_map[(i, j)] = edge
                    edges.append(edge)

        self.sphere_group = VGroup(*nodes)
        self.node_group = VGroup(*node_dots)
        self.edge_group = VGroup(*edges)
        self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

        self.play(Create(self.sphere_group), Create(self.node_group), Create(self.edge_group))
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

        # add labels to nodes
        for i, dot in enumerate(self.node_group):
            label = Tex(f"{i}")
            label.next_to(dot, DOWN if i in [3, 4] else UP) # to avoid sphere-label overlap
            self.play(Create(label))

    def model_measurement(self):
        # zoom into specific party specific qudit
        print()

    def model_individual_EEs(self):
        party_one = self.k_party_obj.state_desc[0] # VERY IMPORTANT!! UNDERSTAND STATE_DESC ATTRIBUTE -- ATM HARD CODED FOR ONE PARTY
        num_qudits = party_one[0]
        for i in range(num_qudits):
            for j in range(i + 1, num_qudits):
                try:
                    print(f"Processing nodes {i} and {j}")

                    # Display EE information
                    my_text = Text(f"Entanglement entropy for nodes {i} and {j}").to_edge(UP)
                    self.play(Create(my_text))
                    self.wait(1)
                    self.play(Uncreate(my_text))

                    # Calculate bipartite entropy
                    A, B = set([i, j]), set(range(num_qudits)) - {i, j}
                    ee = self.k_party_obj.bipartite_entropy(list(A), list(B))
                    
                    '''
                    if self.execution_type == "upper bound":
                        ee = self.entanglement_measures.get_le_lower_bound(self.k_party_obj, A, B)
                    if self.execution_type == "lower bound":
                        ee = self.entanglement_measures.get_le_upper_bound(self.k_party_obj, A, B)
                    '''

                    # Measure and visualize
                    measured = []
                    for state in B:
                        self.measure(state)
                        measured.append(state)
                        self.eeChange(A, measured, ee)
                        self.wait(1)

                    # Display EE results
                    self.display_EE_results(A, B, ee)

                    # Reset the groups for the next iteration
                    self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

                    # Create the copied groups
                    self.play(Create(self.sphere_group_copy), Create(self.node_group_copy), Create(self.edge_group_copy))

                    # Wait for a moment
                    self.wait(1)
                except Exception as e:
                    print(f"Error processing nodes {i} and {j}: {e}")
                    break  # Break the loop if there is an error, remove this if you want to continue to the next pair

    def display_EE_results(self, A, B, ee):
        A_B_text = Text(f"A = {A} B = {B}").scale(0.50).move_to([0, 3, 0])
        ee_text = Text(f"EE: {ee:.4f}").to_edge(DOWN)
        self.play(Create(A_B_text), Create(ee_text))
        self.play(Uncreate(A_B_text), Uncreate(ee_text))

    def measure(self, state):
        sphere = self.sphere_group[state]
        self.measurement_visualization(state)
        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))
        random_color = BLUE if np.random.randint(2) == 0 else RED
        self.node_group[state].set_color(random_color)
        self.play(Create(sphere))
        self.remove_edges(state)

    def remove_edges(self, state):
        for i in range(self.k_party_obj.parties):
            if (state, i) in self.edge_map or (i, state) in self.edge_map:
                edge_delete = self.edge_map.get((state, i)) or self.edge_map.get((i, state))
                self.play(Uncreate(edge_delete))

    def eeChange(self, A, measured, ee):
        state1, state2 = list(A)
        edge = self.edge_map[(state1, state2)]
        edge.set_stroke(width=ee * 2 * edge.get_stroke_width())
        self.play(Create(edge))

    def measurement_visualization(self, state):
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        top_left = np.array([-5, 0, 0])
        scale_factor = 0.75
        rectangle = Rectangle(width=4, height=3, color=WHITE).scale(scale_factor).move_to(top_left)
        sphere = Sphere(radius=1).scale(scale_factor).move_to(top_left)
        letter_m = Text(f"M{state}", font_size=48, color=WHITE).scale(scale_factor).move_to(Square(side_length=2).scale(scale_factor))

        self.play(Create(rectangle), Create(sphere))
        self.play(Create(letter_m))
        self.play(Uncreate(letter_m), Uncreate(sphere), Uncreate(rectangle))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuantumOperationsGUI()
    window.show()
    sys.exit(app.exec())
