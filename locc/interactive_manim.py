import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSlider)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import numpy as np
from qiskit.quantum_info import Statevector, shannon_entropy
from qiskit.circuit.library import XGate, HGate, CXGate
from locc_controller import locc_controller
from k_party import k_party
from locc_operation import locc_operation

from manim import *


class MeasurementScene(ThreeDScene):
    def __init__(self, locc_op, **kwargs):
        self.locc_op = locc_op
        super().__init__(**kwargs)

    def construct(self):
        my_text = Text("EXECUTING " + str(self.locc_op.operation_type) + " on " + str(self.locc_op.party_index) + " party, qudit " + str(self.locc_op.qudit_index))
        my_text.to_edge(UP)
        self.play(Write(my_text))
        self.wait(2)
        self.play(Uncreate(my_text))


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LOCC GUI')
        self.setGeometry(100, 100, 800, 600)

        self.locc_op = locc_operation(1, 0, "measurement")  # Example operation

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.label = QLabel('LOCC Operation', self)
        self.layout.addWidget(self.label)

        self.btn = QPushButton('Execute Measurement Scene', self)
        self.btn.clicked.connect(self.execute_measurement_scene)
        self.layout.addWidget(self.btn)

        self.videoWidget = QVideoWidget(self)
        self.layout.addWidget(self.videoWidget)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Add control buttons
        self.controlLayout = QHBoxLayout()
        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.mediaPlayer.play)
        self.controlLayout.addWidget(self.playButton)

        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.mediaPlayer.pause)
        self.controlLayout.addWidget(self.pauseButton)

        # Add a slider for seeking
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.controlLayout.addWidget(self.positionSlider)

        self.layout.addLayout(self.controlLayout)

        # Connect signals
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def execute_measurement_scene(self):
        # Specify the output file path
        output_file = "measurement_scene.mp4"
        
        # Create a temporary configuration for the scene
        config.media_dir = "."
        config.video_dir = "."
        config.quality = "high_quality"
        config.output_file = output_file

        # Render the scene
        scene = MeasurementScene(self.locc_op)
        scene.render()

        # Play the video in the QVideoWidget
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(output_file))))
        self.mediaPlayer.play()

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    ex.show()
    sys.exit(app.exec_())
