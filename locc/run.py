import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSlider, QMessageBox, QLineEdit, QComboBox, QScrollArea)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import numpy as np
from qiskit.quantum_info import Statevector, shannon_entropy
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import locc_controller
from k_party import k_party
from locc_operation import locc_operation
import copy
from manim import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
import os
from manim import config, Scene
from qiskit import *
from qiskit.quantum_info import Statevector
import numpy as np

class MeasurementScene(ThreeDScene):
    def __init__(self, locc_op, k_party_obj, **kwargs):
        self.locc_op = locc_op
        self.k_party_obj = k_party_obj
        super().__init__(**kwargs)
    
    def construct(self):
        self.initialize_scene()
        self.create_nodes_and_edges()
        self.add_labels_to_nodes()
        self.model_individual_EEs()
    
    def initialize_scene(self):
        my_text = Text(f"EXECUTING {self.locc_op.operation_type} on party {self.locc_op.party_index}, qudit {self.locc_op.qudit_index}")
        # my_text = Text("Modeling Entanglement Entropy: GHZ State").to_edge(ORIGIN)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))
        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)

    def create_nodes_and_edges(self):
        numParties = self.k_party_obj.parties
        nodes = [Sphere(radius=0.3, color=BLUE) for _ in range(numParties)]
        coordinates = [(2 * np.cos(angle), 2 * np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, numParties, endpoint=False)]

        for node, coord in zip(nodes, coordinates):
            node.move_to(coord)

        node_dots = [Dot(point=coord) for coord in coordinates]
        edges, self.edge_map = self.initialize_edges(numParties, node_dots)

        self.sphere_group = VGroup(*nodes)
        self.node_group = VGroup(*node_dots)
        self.edge_group = VGroup(*edges)
        self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

        self.play(Create(self.sphere_group), Create(self.node_group), Create(self.edge_group))
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

    def initialize_edges(self, numParties, node_dots):
        edges, self.edge_map = [], {}
        for i in range(numParties):
            for j in range(i + 1, numParties):
                if (j, i) not in self.edge_map:
                    edge = Line(node_dots[i].get_center(), node_dots[j].get_center())
                    self.edge_map[(i, j)] = edge
                    edges.append(edge)
        return edges, self.edge_map

    def add_labels_to_nodes(self):
        for i, dot in enumerate(self.node_group):
            label = Tex(f"{i}")
            label.next_to(dot, DOWN if i in [3, 4] else UP)
            self.play(Create(label))

    def model_individual_EEs(self):
        numParties = self.k_party_obj.parties
        for i in range(numParties):
            for j in range(i + 1, numParties):
                try:
                    print(f"Processing nodes {i} and {j}")

                    # Display EE information
                    self.display_EE_info(i, j)

                    # Calculate bipartite entropy
                    A, B = set([i, j]), set(range(numParties)) - {i, j}
                    ee = self.k_party_obj.bipartite_entropy(list(A), list(B))

                    # Display EE results
                    self.display_EE_results(A, B, ee)

                    # Measure and visualize
                    self.measure_and_visualize(A, B, ee)

                    # Reset the groups for the next iteration
                    self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

                    # Create the copied groups
                    self.play(Create(self.sphere_group_copy), Create(self.node_group_copy), Create(self.edge_group_copy))

                    # Wait for a moment
                    self.wait(1)
                except Exception as e:
                    print(f"Error processing nodes {i} and {j}: {e}")
                    break  # Break the loop if there is an error, remove this if you want to continue to the next pair

    def display_EE_info(self, i, j):
        my_text = Text(f"Entanglement entropy for nodes {i} and {j}").to_edge(UP)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))

    def display_EE_results(self, A, B, ee):
        A_B_text = Text(f"A = {A} B = {B}").scale(0.50).move_to([0, 3, 0])
        ee_text = Text(f"EE: {ee:.4f}").to_edge(DOWN)
        self.play(Create(A_B_text), Create(ee_text))
        self.play(Uncreate(A_B_text), Uncreate(ee_text))

    def measure_and_visualize(self, A, B, ee):
        measured = []
        for state in B:
            self.measure(state)
            measured.append(state)
            self.eeChange(A, measured, ee)
            self.wait(1)

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

class VideoThread(QThread):
    video_generated = pyqtSignal(str)

    def __init__(self, locc_operation, k_party_instance, video_path, parent=None):
        super(VideoThread, self).__init__(parent)
        self.locc_operation = locc_operation
        self.k_party_instance = k_party_instance
        self.video_path = video_path

    def run(self):
        # Specify the output file path
        config.media_dir = "."
        config.video_dir = "."
        config.quality = "medium_quality"  # Adjust as needed
        config.output_file = self.video_path

        # Render the scene
        scene = MeasurementScene(self.locc_operation, self.k_party_instance)
        scene.render()

        # Emit the signal with the video path
        self.video_generated.emit(self.video_path)

class QuantumOperationsGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # INITIALIZE BASIC GUI ELEMENTS 
        self.setWindowTitle("Quantum Operations")
        self.setGeometry(100, 100, 800, 600)  # Set a larger window size

        self.locc_op = locc_operation(1, 0, "measurement")  # example operation

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # LOCC Operation Creator
        self.create_locc_operation_ui(self.scroll_layout)

        # k_party Creator
        self.create_k_party_ui(self.scroll_layout)

        # manim video creator
        self.videoWidget = QVideoWidget(self)
        self.scroll_layout.addWidget(self.videoWidget)
        self.videoWidget.setMinimumSize(640, 480)  # Set a minimum size for the video widget

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Add control buttons
        controlLayout = QHBoxLayout()
        playButton = QPushButton('Play')
        playButton.clicked.connect(self.mediaPlayer.play)
        controlLayout.addWidget(playButton)

        pauseButton = QPushButton('Pause')
        pauseButton.clicked.connect(self.mediaPlayer.pause)
        controlLayout.addWidget(pauseButton)

        # Add a slider for seeking
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        controlLayout.addWidget(self.positionSlider)

        self.scroll_layout.addLayout(controlLayout)

        # Connect signals
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        # Execute Protocol Button
        execute_button = QPushButton("Execute Protocol")
        execute_button.clicked.connect(self.execute_measurement_scene)
        self.scroll_layout.addWidget(execute_button)

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

    @pyqtSlot(str)
    def on_video_generated(self, video_path):
        # Ensure the video file exists
        if not os.path.exists(video_path):
            QMessageBox.critical(self, "Error", f"Video file {video_path} not found.")
            return

        # Play the video in the QVideoWidget
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(video_path))))
        self.mediaPlayer.play()
        QMessageBox.information(self, "Protocol Executed", "The protocol has been executed successfully.")

    def execute_measurement_scene(self):
        if self.k_party_instance is None:
            QMessageBox.critical(self, "Error", "k_party instance not created.")
            return
        
        if self.locc_operation_instance is None:
            QMessageBox.critical(self, "Error", "locc_operation instance not created.")
            return
        
        # Create locc_controller instance and execute protocol
        controller = locc_controller(self.locc_operation_instance, self.k_party_instance)
        controller.execute_protocol()

        # Specify the output file path
        output_file = "measurement_scene.mp4"

        # Create and start the video generation thread
        self.video_thread = VideoThread(self.locc_operation_instance[0], self.k_party_instance, output_file)
        self.video_thread.video_generated.connect(self.on_video_generated)
        self.video_thread.start()
    
    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuantumOperationsGUI()
    window.show()
    sys.exit(app.exec_())
