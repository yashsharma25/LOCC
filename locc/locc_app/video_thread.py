from PyQt5.QtCore import QThread, pyqtSignal
from measurement_scene import MeasurementScene

class VideoThread(QThread):
    video_generated = pyqtSignal(str)

    def __init__(self, locc_operations, k_party, output_file, res, execution_type, ee_string, new_k_party_obj):
        super().__init__()
        self.locc_operations = locc_operations
        self.k_party = k_party
        self.output_file = output_file
        self.res = res
        self.execution_type = execution_type
        self.ee_string = ee_string
        self.new_k_party_obj = new_k_party_obj

    def run(self):
        MeasurementScene(self.locc_operations, self.k_party, self.res, self.execution_type, self.ee_string, self.new_k_party_obj).render(self.output_file)
        self.video_generated.emit(self.output_file)
