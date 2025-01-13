import sys
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.quantum_model import QuantumModel
from model.video_model import VideoModel
import subprocess
import os
import platform

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.quantum_model = QuantumModel()  # Create the model
        self.video_model = VideoModel() # New video model
        self.view = MainWindow(self)  # Pass the controller to the view

    def run(self):
        # Show the main window and start the event loop
        self.view.show()
        sys.exit(self.app.exec_())

    def get_input_for_video_and_call_video(self):
        """
        Generate a Manim video by delegating to the model and updating the view.
        """
        locc_protocol, k_party, execution_type = self.quantum_model.get_input_for_video() # to ensure locc procotol and k party objs are created with our quantum model

        try:
            video_path = self.video_model.generate_video(locc_protocol, k_party, execution_type)
            return video_path
        except Exception as e:
            return f"Error generating video: {str(e)}"
    
    def play_video_with_os_player(self, video_path):
        """
        Play the generated video using the user's operating system video player.
        """
        try:
            if platform.system() == "Windows":
                os.startfile(video_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", video_path])
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", video_path])
        except Exception as e:
            self.view.display_message(f"Could not play video: {str(e)}")

    def perform_operation(self, operation_name, *args):
        """
        Handle operations requested by the view, e.g., manipulating quantum states.
        """
        if operation_name == "create_quantum_state":
            result = self.quantum_model.create_quantum_state(*args) 
            self.view.display_message(f"Initialized state: {result}")
        elif operation_name == "generate_state_desc_label_and_k_party":
            result = self.quantum_model.generate_state_desc_label_and_k_party(*args)
            self.view.display_message(f"{result}")
        elif operation_name == "save_locc_operation":
            result = self.quantum_model.save_locc_operation(*args)
            self.view.display_message(f"{result}")
        elif operation_name == "handle_default_operator":
            # TODO: make method in model to handle this perform op...
            print() # Don't think we need this...
        elif operation_name == "execute_protocol":
            self.quantum_model.save_execution_type(*args)
            result = self.get_input_for_video_and_call_video()
            if result[0] == "E": # to ensure it's the error message
                self.view.display_message(f"{result}")
            else:
                self.play_video_with_os_player(result)
        else:
            self.view.display_message(f"Unknown operation: {operation_name}")
