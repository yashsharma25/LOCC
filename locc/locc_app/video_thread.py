from manim import config
from PyQt5.QtCore import QThread, pyqtSignal
from measurement_scene import MeasurementScene

class VideoThread(QThread):

    '''
    Args:

    locc_protocol: an array of locc_op objects
    k_party: an object of class k_party
    output_file: where resulting video will be saved
    ee_strings: array of strings where each string corresponds to the resulting ee between party involved in measurement and the rest of the k party system
    new_k_party_obj: the resulting k party obj after the given locc protocol has been executed on the given k party
    
    '''
    video_generated = pyqtSignal(str)
    new_k_party_generated = pyqtSignal(object)

    # self.video_thread = VideoThread(self.locc_protocol_obj, self.k_party_obj, output_file, ee_strings, new_k_party_obj)

    def __init__(self, locc_protocol, k_party, output_file, execution_type):
        super().__init__()
        self.locc_protocol = locc_protocol
        self.k_party = k_party
        self.output_file = output_file
        self.execution_type = execution_type

    def run(self):
        config.quality = "low_quality"
        measurement_scene = MeasurementScene(self.locc_protocol, self.k_party, self.execution_type)
        measurement_scene.render(self.output_file)
        new_k_party_obj = measurement_scene.get_new_k_party_obj()
        self.video_generated.emit(self.output_file)
        self.new_k_party_generated.emit(new_k_party_obj)