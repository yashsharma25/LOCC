from manim import *

class VisualizeLOCC(Scene):
    def construct(self):
        # Example parameters for the visualization
        num_parties = 2  # Number of parties
        qudits_per_party = [3, 4]  # Number of qudits for each party
        qudit_radius = 0.3
        spacing = 1.5
        
        # Create spheres for each party
        party_graphs = []
        for party_index in range(num_parties):
            spheres = self.create_spheres(party_index, qudits_per_party[party_index], qudit_radius, spacing)
            party_graphs.append(spheres)
        
        # Position the party graphs
        for i, graph in enumerate(party_graphs):
            graph.move_to(RIGHT * i * (spacing + 2))

        # Add spheres to the scene
        for graph in party_graphs:
            self.play(*[Create(sphere) for sphere in graph])
        
        # Simulate measurement
        self.simulate_measurement(party_graphs)

    def create_spheres(self, party_index, num_qudits, radius, spacing):
        spheres = VGroup()
        for i in range(num_qudits):
            sphere = Sphere(radius=radius)
            sphere.set_fill(BLUE, opacity=0.7)
            sphere.set_stroke(WHITE, width=2)
            sphere.move_to(LEFT * spacing * (num_qudits / 2 - i))  # Center the spheres
            spheres.add(sphere)
        return spheres

    def simulate_measurement(self, party_graphs):
        # Simulate the measurement by shrinking the spheres
        for party_graph in party_graphs:
            for sphere in party_graph:
                self.play(sphere.animate.scale(0.5), run_time=0.5)
                self.wait(0.2)

# To run this script, save it to a file and execute it with MANIM
# Example command: manim -pql your_script.py VisualizeLOCC
