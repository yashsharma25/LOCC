from entanglement_measures import EntanglementMeasures
from locc_controller import locc_controller

class ExecuteProtocolController:
    def __init__(self, locc_protocol_obj, k_party_obj, execution_type, party_A, party_B):
        self.locc_protocol_obj = locc_protocol_obj
        self.k_party_obj = k_party_obj
        self.execution_type = execution_type
        self.party_A = party_A
        self.party_B = party_B
        self.ee_string = ""

    def execute_protocol(self):
        if not self.locc_protocol_obj or not self.k_party_obj:
            raise ValueError("LOCC Operation or K Party instance not created.")
        
        if self.party_A == self.party_B:
            raise ValueError("Party A and Party B must be different for entanglement measures.")
        
        locc_controller = locc_controller(self.locc_protocol_obj, self.k_party_obj)
        new_k_party_obj = locc_controller.execute_protocol()
        entanglement_measures = self.create_entanglement_measures()
        
        output_file = "measurement_scene.mp4"
        return output_file, entanglement_measures, new_k_party_obj

    def create_entanglement_measures(self):
        entanglement_measures = EntanglementMeasures(self.k_party_obj.dims, self.k_party_obj.q_state, party_to_measure=None)
        entanglement_measures.partyA = self.party_A
        entanglement_measures.partyB = self.party_B

        if self.execution_type == "upper bound":
            self.ee_string = entanglement_measures.get_le_upper_bound(self.k_party_obj, self.party_A, self.party_B)
        elif self.execution_type == "lower bound":
            self.ee_string = entanglement_measures.get_le_lower_bound(self.k_party_obj, self.party_A, self.party_B)

        return entanglement_measures