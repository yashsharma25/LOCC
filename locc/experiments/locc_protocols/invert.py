from qiskit.extensions import Initialize

#reverse operations useful to verify teleportation protocols
class invert:
    def __init__(self, psi):
        self.init_gate = Initialize(psi)
        self.init_gate.label = "init"
        self.inverse_init_gate =  self.init_gate.gates_to_uncompute()


    def invert(self, psi, qudit_index):
        psi = psi.evolve(self.inverse_init_gate, [qudit_index])
        return psi